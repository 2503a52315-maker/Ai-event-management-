import qrcode
import os


def generate_qr(registration_id):
    data = f"REGISTRATION:{registration_id}"

    qr = qrcode.make(data)

    os.makedirs("generated_qr", exist_ok=True)

    filename = f"generated_qr/qr_registration_{registration_id}.png"

    qr.save(filename)

    return filename