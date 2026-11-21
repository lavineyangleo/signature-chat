import base64
import json
import time
import urllib.error
import urllib.request


class ProviderError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def decode_response(raw: bytes) -> bytes:
    """Read completed JSON/SSE responses. Never treat a partial image as success."""
    text = raw.decode('utf-8-sig')
    try:
        records = [json.loads(text)]
    except json.JSONDecodeError:
        records, lines = [], []
        for line in text.splitlines() + ['']:
            if line.startswith('data:'):
                lines.append(line[5:].lstrip())
            elif not line and lines:
                payload = '\n'.join(lines)
                lines = []
                if payload != '[DONE]':
                    records.append(json.loads(payload))
    completed, finished_items = [], []
    for record in records:
        if record.get('type') in ('response.failed', 'response.incomplete', 'error') or record.get('error'):
            raise ProviderError('服务端报告生成失败或不完整；未自动重试。')
        if record.get('type') == 'response.completed':
            completed.append(record.get('response', {}))
        elif record.get('object') == 'response' and record.get('status') == 'completed':
            completed.append(record)
        elif record.get('type') == 'response.output_item.done':
            item = record.get('item', {})
            if item.get('status') == 'completed':
                finished_items.append(item)
    if completed:
        candidates = [item for response in completed for item in response.get('output', [])] + finished_items
        for item in candidates:
            if item.get('type') == 'image_generation_call' and item.get('result'):
                try:
                    return base64.b64decode(item['result'], validate=True)
                except (ValueError, TypeError) as exc:
                    raise ProviderError('服务端图片编码无效。') from exc
    raise ProviderError('未收到完整图片结果；可能已产生用量，未自动重试。')


class C2AProvider:
    def __init__(self, key: str, model: str = 'gpt-image-2', main_model: str = 'gpt-6.1-sol'):
        self.key = key
        self.model = model
        self.main_model = main_model

    @property
    def configured(self):
        return bool(self.key.strip())

    def generate(self, prompt: str) -> bytes:
        if not self.configured:
            raise ProviderError('请先设置 C2A_API_KEY 环境变量并重启程序。')
        body = {'model': self.main_model, 'input': prompt, 'stream': True,
                'tools': [{'type': 'image_generation', 'model': self.model,
                           'output_format': 'png', 'background': 'transparent'}]}
        request = urllib.request.Request('https://c2a.jiaopilot.com/v1/responses',
            data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
            headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        started = time.monotonic()
        try:
            with opener.open(request, timeout=30) as response:
                chunks, length = [], 0
                while True:
                    if time.monotonic() - started > 180:
                        raise ProviderError('生成超时；可能已产生用量，未自动重试。')
                    chunk = response.read1(65536)
                    if not chunk:
                        break
                    length += len(chunk)
                    if length > 64 * 1024 * 1024:
                        raise ProviderError('响应超过64MB限制。')
                    chunks.append(chunk)
            return decode_response(b''.join(chunks))
        except urllib.error.HTTPError as exc:
            # Never include the server body, headers, key or request in public errors.
            raise ProviderError(f'C2A 返回 HTTP {exc.code}；检查凭证或服务状态。未自动重试。') from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderError('网络中断或超时；可能已产生用量，未自动重试。') from None
