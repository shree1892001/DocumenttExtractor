from PIL import Image, ImageDraw

def generate_sample_photo(path="license_photo.jpg"):
    img = Image.new("RGB", (160, 200), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)

    # Head & Shoulders dummy drawing
    draw.rectangle([20, 40, 140, 160], fill=(180, 180, 180))
    draw.ellipse([50, 60, 110, 120], fill=(150, 150, 150))  # head
    draw.text((55, 140), "PHOTO", fill="black")

    img.save(path)
    print(f"✅ Sample photo saved as: {path}")

generate_sample_photo()
