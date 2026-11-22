import os
import tempfile
import unittest
import uuid
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from signature_chat.core.prompt import build_prompt
from signature_chat.core.styles import design_policy
from signature_chat.core.transparency import transparent_signature
from signature_chat.infra.provider import C2AProvider, decode_response, ProviderError
from signature_chat.infra.store import Store
from signature_chat.services.studio import Studio, valid_id

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'assets/styles-transparent.png'


class TransparentExportTests(unittest.TestCase):
    def test_real_pastel_native_alpha_and_rgb_survive(self):
        source = ROOT / 'assets/illustrated-transparent.png'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'color.png'
            metadata = transparent_signature(source, output, preserve_color=True)
            self.assertEqual(metadata['processing'], 'color-preserving-alpha-v1')
            with Image.open(source) as original, Image.open(output) as result:
                self.assertEqual(original.tobytes(), result.tobytes())
                red, green, blue, alpha = result.split()
                self.assertGreater(ImageChops.difference(red, blue).getextrema()[1], 20)
                self.assertEqual(alpha.getextrema(), (0, 255))

    def test_real_pastel_white_fallback_retains_color(self):
        with tempfile.TemporaryDirectory() as tmp, Image.open(ROOT / 'assets/illustrated-transparent.png') as ink:
            white = Image.new('RGBA', ink.size, 'white')
            white.alpha_composite(ink)
            source, target = Path(tmp) / 'white.png', Path(tmp) / 'result.png'
            white.convert('RGB').save(source)
            transparent_signature(source, target, preserve_color=True)
            with Image.open(target) as result:
                red, green, blue, alpha = result.split()
                self.assertGreater(ImageChops.difference(red, blue).getextrema()[1], 20)
                self.assertEqual(alpha.getextrema(), (0, 255))
                recomposed = Image.new('RGBA', result.size, 'white')
                recomposed.alpha_composite(result)
                error = ImageStat.Stat(ImageChops.difference(recomposed.convert('RGB'), white.convert('RGB')))
                self.assertLess(max(error.mean), 1)

    def test_real_showcase_has_actual_alpha(self):
        for name in ('styles-transparent.png', 'bilingual-transparent.png'):
            with Image.open(ROOT / 'assets' / name) as image:
                self.assertEqual(image.mode, 'RGBA')
                self.assertEqual(image.getchannel('A').getextrema(), (0, 255))
                self.assertGreater(image.getchannel('A').histogram()[0], image.width * image.height // 2)

    def test_white_background_roundtrip_of_real_ink(self):
        with tempfile.TemporaryDirectory() as tmp, Image.open(SAMPLE) as ink:
            white = Image.new('RGBA', ink.size, 'white')
            white.alpha_composite(ink)
            source = Path(tmp) / 'white.png'
            target = Path(tmp) / 'transparent.png'
            white.convert('RGB').save(source)
            metadata = transparent_signature(source, target)
            self.assertEqual((metadata['width'], metadata['height']), ink.size)
            with Image.open(target) as result:
                diff = ImageChops.difference(result.getchannel('A'), ink.getchannel('A'))
                self.assertLess(ImageStat.Stat(diff).mean[0], 0.1)
                self.assertEqual(result.getchannel('A').getextrema(), (0, 255))

    def test_transparent_real_image_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'result.png'
            transparent_signature(SAMPLE, output)
            with Image.open(output) as a, Image.open(SAMPLE) as b:
                self.assertIsNone(ImageChops.difference(a, b).getbbox())


class ConversationTests(unittest.TestCase):
    def test_illustrated_styles_and_color_override(self):
        pet = build_prompt(['给 Lavine 设计签名【风格：萌宠线描，小猫融入笔画】'])
        self.assertIn('animal line-art', pet)
        self.assertNotIn('Default comparison:', pet)
        pastel = ['给 Lavine 设计签名【风格：淡彩萌系，保留粉色】']
        self.assertTrue(design_policy(pastel)['preserve_color'])
        self.assertNotIn('BLACK INK ONLY', build_prompt(pastel))
        self.assertFalse(design_policy(pastel + ['改为黑白'])['preserve_color'])
        self.assertFalse(design_policy(pastel + ['【风格：简洁易读，只生成这一款】'])['preserve_color'])
        self.assertFalse(design_policy(pastel + ['【风格：同一姓名分别生成简洁易读、回环花式、利落速签三款对照】'])['illustrated'])

    def test_context_preserves_exact_name_and_change(self):
        prompt = build_prompt(['给 Lavine 设计签名', '只保留一款，收笔短一点'])
        self.assertIn('Lavine', prompt)
        self.assertIn('只保留一款', prompt)
        self.assertIn('BLACK INK ONLY', prompt)

    def test_invalid_messages_and_ids(self):
        for messages in ([], [''], [None], ['x' * 2001]):
            with self.assertRaises(ValueError):
                build_prompt(messages)
        for value in ('../private', '', None):
            with self.assertRaises(ValueError):
                valid_id(value)

    def test_missing_credential_does_not_create_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp))
            studio = Studio(store, C2AProvider(''))
            with self.assertRaises(ValueError):
                studio.submit({'id': str(uuid.uuid4()), 'session': str(uuid.uuid4()), 'message': '给 Lavine 设计签名'})
            self.assertEqual(store.rows(), [])

    def test_restart_marks_unfinished_record_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root)
            key, session = str(uuid.uuid4()), str(uuid.uuid4())
            store.add(key, session, '给 Lavine 设计签名')
            recovered = Store(root)
            self.assertEqual(recovered.rows(session)[0]['status'], 'interrupted')
            studio = Studio(recovered, C2AProvider(''))
            existing = studio.submit({'id': key, 'session': session, 'message': '给 Lavine 设计签名'})
            self.assertEqual(existing['status'], 'interrupted')
            self.assertEqual(len(recovered.rows()), 1)


class ResponseTests(unittest.TestCase):
    def test_incomplete_or_invalid_response_is_not_success(self):
        with self.assertRaises(ProviderError):
            decode_response(b'data: [DONE]\n\n')
        with self.assertRaises((ValueError, ProviderError)):
            decode_response(b'not a response')

    @unittest.skipUnless(os.environ.get('SIGNATURE_REAL_RESPONSE'), 'Optional private real-response replay; no fabricated API fixtures')
    def test_actual_historical_response(self):
        raw = Path(os.environ['SIGNATURE_REAL_RESPONSE']).read_bytes()
        image = decode_response(raw)
        with tempfile.TemporaryDirectory() as tmp:
            result = transparent_signature(image, Path(tmp) / 'signature.png')
            self.assertGreater(result['transparent_pixels'], 0)
            self.assertEqual(result['mode'], 'RGBA')


if __name__ == '__main__':
    unittest.main()
