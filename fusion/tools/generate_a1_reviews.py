"""Publish the A1-sized variant with the user-tested direct review URL."""
import ast
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import cv2
import numpy as np
import qrcode

from render_a1_preview import render_a1_preview

ROOT=Path(__file__).resolve().parents[2]
GOOGLE_URL='https://search.google.com/local/writereview?placeid=ChIJvVHxDlBCGQ0Rcw8jp4G4TNg'


def main():
    # M keeps the 64 mm field at 45 modules including the quiet zone, instead
    # of 53 with Q. No artwork/logo is placed inside the code.
    qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                     box_size=24,border=4)
    qr.add_data(GOOGLE_URL)
    qr.make(fit=True)
    rows=[''.join('1' if value else '0' for value in row) for row in qr.get_matrix()]
    assert len(rows)==45
    decoded,_,_=cv2.QRCodeDetector().detectAndDecode(
        np.array(qr.make_image().convert('L')))
    assert decoded==GOOGLE_URL

    source=(ROOT/'fusion/EssencialA1/EssencialA1.py').read_text()
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='GOOGLE_ROWS' for t in n.targets))
    old=ast.get_source_segment(source,node)
    new='GOOGLE_ROWS = [\n'+''.join('    '+repr(row)+',\n' for row in rows)+']'
    assert source.count(old)==1
    source=source.replace(old,new,1)
    source=source.replace('import adsk.fusion\n',
        'import adsk.fusion\n\nGOOGLE_REVIEW_URL = '+repr(GOOGLE_URL)+
        "\nGOOGLE_QR_ERROR_CORRECTION = 'M'\n",1)
    source=source.replace('Clínica Essencial A1 v5','Clínica Essencial A1 Reviews v6')
    source=source.replace('Clinica Essencial A1 V5','Clinica Essencial A1 Reviews V6')
    source=source.replace('A1 V5 created','A1 Reviews V6 created')
    source=source.replace('A1 V5 failed','A1 Reviews V6 failed')
    old_message='Google QR still uses search/share link; direct review link is pending.'
    assert old_message in source
    source=source.replace(old_message,
        'Google QR opens the confirmed review form. Program lower NFC tag with same URL.')
    ast.parse(source)
    folder=ROOT/'fusion/EssencialA1Reviews'
    folder.mkdir(exist_ok=True)
    script=folder/'EssencialA1Reviews.py'
    script.write_text(source)
    preview=ROOT/'designs/essencial-a1-avaliacoes-esquema.png'
    values=render_a1_preview(source,preview,GOOGLE_URL,'Google: formulário direto de avaliação')
    assert values['QR_SIZE']==64
    assert values['GOOGLE_ROWS']==rows

    # A JPG matching this exact printed matrix is also included for testing.
    jpg=ROOT/'designs/google-reviews-qr-print.jpg'
    qr.make_image(fill_color='black',back_color='white').convert('RGB').save(
        jpg,format='JPEG',quality=100,subsampling=0)
    decoded,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(jpg)))
    assert decoded==GOOGLE_URL
    package=ROOT/'downloads/essencial-fusion-a1-avaliacoes.zip'
    with ZipFile(package,'w',ZIP_DEFLATED) as z:
        z.write(script,'EssencialA1Reviews/EssencialA1Reviews.py')
        z.write(folder/'README.md','README.md')
        z.write(preview,'essencial-a1-avaliacoes-esquema.png')
        z.write(jpg,'google-reviews-qr-print.jpg')
    with ZipFile(package) as z:
        assert z.testzip() is None
        assert z.read('EssencialA1Reviews/EssencialA1Reviews.py')==script.read_bytes()
    print('A1 Reviews: envelope 208 x 242 mm, QR 64 mm, Google direct review URL.')
    print('Google ECC M, matrix 45 including border, module pitch %.3f mm.' %
          (64/len(rows)))
    print('Both preview QR and saved Google JPG decoded successfully; ZIP verified.')


if __name__=='__main__':
    main()
