import threading
import uuid
from signature_chat.core.prompt import build_prompt
from signature_chat.core.styles import design_policy
from signature_chat.core.transparency import transparent_signature
from signature_chat.infra.provider import ProviderError


def valid_id(value):
    if not isinstance(value, str) or str(uuid.UUID(value)) != value:
        raise ValueError('无效对话或请求编号。')
    return value


class Studio:
    def __init__(self, store, provider):
        self.store, self.provider = store, provider
        self.lock = threading.Lock()
        self.active = False

    def submit(self, body):
        key, session = valid_id(body.get('id')), valid_id(body.get('session'))
        message = body.get('message')
        build_prompt([message])
        with self.lock:
            rows = self.store.rows()
            prior = next((r for r in rows if r['id'] == key), None)
            if prior:
                if prior['session'] != session or prior['message'] != message:
                    raise ValueError('请求编号已被其他内容使用。')
                return prior
            if self.active:
                raise ValueError('已有签名正在生成，请稍候。')
            if not self.provider.configured:
                raise ValueError('请设置 C2A_API_KEY 环境变量并重启程序。')
            messages = [r['message'] for r in rows if r['session'] == session] + [message]
            prompt = build_prompt(messages)
            policy = design_policy(messages)
            self.store.add(key, session, message)
            self.active = True

        def run():
            try:
                raw = self.provider.generate(prompt)
                output = self.store.root / 'images' / f'{key}.png'
                metadata = transparent_signature(raw, output, preserve_color=policy['preserve_color'])
                metadata['style'] = policy['style']
                metadata['requested_model'] = self.provider.model
                self.store.finish(key, 'success', metadata)
            except ProviderError as exc:
                self.store.finish(key, 'failed', error=str(exc))
            except Exception:
                self.store.finish(key, 'failed', error='图片处理未完成；请检查服务状态。未自动重试。')
            finally:
                with self.lock:
                    self.active = False

        threading.Thread(target=run, daemon=True).start()
        return next(r for r in self.store.rows(session) if r['id'] == key)
