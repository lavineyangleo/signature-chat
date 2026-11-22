import argparse
import os
from pathlib import Path
from signature_chat.core.transparency import transparent_signature
from signature_chat.infra.provider import C2AProvider
from signature_chat.infra.store import Store
from signature_chat.services.studio import Studio
from signature_chat.server import serve


def main():
    parser = argparse.ArgumentParser(description='Signature Chat — Vue signature studio with transparent PNG exports')
    sub = parser.add_subparsers(dest='command', required=True)
    server = sub.add_parser('serve', help='Run the local Vue application and API')
    server.add_argument('--port', type=int, default=8780)
    server.add_argument('--data-dir', type=Path, default=Path.home() / '.signature-chat')
    server.add_argument('--model', choices=('gpt-image-2', 'gpt-image-2.5-flare', 'gpt-image-2.5-sunburst'), default='gpt-image-2')
    matte = sub.add_parser('transparent', help='Convert monochrome white-background artwork into transparent PNG')
    matte.add_argument('input', type=Path)
    matte.add_argument('output', type=Path)
    matte.add_argument('--preserve-color', action='store_true', help='Keep pastel ink and illustration fills')
    args = parser.parse_args()
    if args.command == 'transparent':
        if args.input.resolve() == args.output.resolve() or args.output.exists():
            parser.error('Choose a new output path; existing files are not overwritten.')
        if args.output.suffix.lower() != '.png':
            parser.error('The output must use the .png extension.')
        metadata = transparent_signature(args.input, args.output, preserve_color=args.preserve_color)
        print(f"Transparent PNG: {metadata['width']}x{metadata['height']}; RGBA; {metadata['transparent_pixels']} transparent pixels")
    else:
        if not 1 <= args.port <= 65535:
            parser.error('Port must be between 1 and 65535.')
        provider = C2AProvider(os.environ.get('C2A_API_KEY', ''), args.model, os.environ.get('C2A_MAIN_MODEL', 'gpt-6.1-sol'))
        serve(Studio(Store(args.data_dir), provider), args.port)


if __name__ == '__main__':
    main()
