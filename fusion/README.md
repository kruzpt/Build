# Clínica Essencial — Fusion concept

1. Extract the ZIP, keeping the `EssencialDraft` folder and its Python file together.
2. Open Autodesk Fusion and switch to the Design workspace.
3. Open Utilities → Scripts and Add-Ins (or search for that command with S).
4. In Scripts, use the + / Add command to select the `EssencialDraft` folder.
5. Select EssencialDraft and Run. It creates a new document.
6. Save the result as an .f3d file.

The panel lies in XY; Z is its thickness. Use a front/top view normal to XY
to see the layout. All editable constants at the start of the script use mm.

Draft dimensions: 180 × 220 × 5 mm panel; 76 mm logo circle centered at
(28, 220), extending beyond the upper-left edge. The panel and logo silhouette
are a single body. The stylised E and sparkle are separate flush colour inlays.
The base is a separate part, shown assembled, with a 5.3 mm slot.
The NFC rear recess is 26 mm diameter with a 1 mm front wall; confirm your
physical tag size before manufacturing. No NFC electronics are supplied.

QR is a blank placeholder, not a generated code. Labels are visible sketch
text, not printable embossed lettering. Logo is an approximation, not exact
vector artwork. Vertebrae are simplified rectangular reliefs. Final fillets,
anatomical shaping, exact branding and manufacturing checks remain to be done.

Python syntax was checked in the cloud. Fusion APIs and generated geometry
cannot be executed or validated here; run this draft in Fusion before export.
If creation fails, copy the full error dialog for diagnosis.
