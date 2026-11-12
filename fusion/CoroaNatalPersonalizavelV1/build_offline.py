"""Bundle the offline form; reuse a complete, previously sliced A1 PLA profile."""
from pathlib import Path
from zipfile import ZipFile
import base64
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'downloads/anilha-aquela-v2-LOBO-A1-04-AMS-4-cores.3mf'
TARGET = ROOT / 'downloads/coroa-natal-v1-personalizar.html'


def main():
    with ZipFile(SOURCE) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
    assert settings['printer_settings_id'] == 'Bambu Lab A1 0.4 nozzle'
    assert settings['filament_type'] == ['PLA'] * 4
    assert settings['layer_height'] == '0.12'
    settings.update({
        'print_settings_id': 'Coroa Natal V1 A1 0.12 PLA AMS',
        'filament_settings_id': [f'Generic PLA {name} @BBL A1 0.4' for name in ['Creme', 'Verde escuro', 'Verde claro', 'Vermelho']],
        'filament_colour': ['#F4E5C4', '#234E3A', '#719071', '#B51636'],
        'filament_multi_colour': ['#F4E5C4', '#234E3A', '#719071', '#B51636'],
    })
    (HERE / 'bambu-settings.json').write_text(json.dumps(settings, ensure_ascii=False, indent=2) + '\n')
    assets = {'settings': settings, 'fonts': {
        name: base64.b64encode((HERE / 'fonts' / filename).read_bytes()).decode()
        for name, filename in [('Pacifico', 'Pacifico-Regular.ttf'), ('LeckerliOne', 'LeckerliOne-Regular.ttf')]
    }}
    files = ['vendor/clipper-lib.js', 'vendor/earcut.js', 'vendor/opentype.js', 'vendor/fflate.js', 'geometry.js', 'export3mf.js']
    scripts = ''.join('<script>\n' + (HERE / file).read_text().replace('</script', '<\\/script') + '\n</script>\n' for file in files)
    scripts += '<script>const COROA_ASSETS=' + json.dumps(assets, ensure_ascii=True) + ';</script>\n'
    licenses = {p.name: p.read_text() for p in list((HERE/'fonts').glob('*OFL.txt')) + list((HERE/'vendor').glob('*LICENSE.txt'))}
    scripts += '<script type="application/json" id="third-party-licenses">' + json.dumps(licenses, ensure_ascii=True).replace('<', '\\u003c') + '</script>\n'
    scripts += '<script>' + (HERE / 'app.js').read_text() + '</script>'
    text = (HERE / 'app.html').read_text().replace('<!-- BUNDLE -->', scripts)
    TARGET.write_text(text)
    provenance = {'source_3mf': str(SOURCE.relative_to(ROOT)), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  'changes_from_source_profile': ['process name', 'filament names', 'display colors'],
                  'filament_calibration': 'Generic PLA; no calibration transferred from another spool',
                  'html_sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest()}
    (HERE / 'profile-source.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(TARGET, TARGET.stat().st_size)


if __name__ == '__main__':
    main()
