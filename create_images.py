from PIL import Image, ImageDraw, ImageFont
import os

def create_door_image():
    # Create a brown door with decorative panels
    img = Image.new('RGB', (200, 300), '#8B4513')
    draw = ImageDraw.Draw(img)
    
    # Door panels
    draw.rectangle([20, 20, 180, 140], fill='#A0522D', outline='#654321', width=2)
    draw.rectangle([20, 160, 180, 280], fill='#A0522D', outline='#654321', width=2)
    
    # Door handle
    draw.ellipse([150, 140, 170, 160], fill='#FFD700')
    
    return img

def create_car_image():
    # Create a simple car silhouette
    img = Image.new('RGB', (180, 280), '#34495E')
    draw = ImageDraw.Draw(img)
    
    # Car body
    draw.rectangle([30, 100, 150, 160], fill='#E74C3C')
    draw.rectangle([60, 70, 120, 100], fill='#E74C3C')
    
    # Wheels
    draw.ellipse([40, 140, 70, 170], fill='#2C3E50')
    draw.ellipse([110, 140, 140, 170], fill='#2C3E50')
    
    return img

def create_goat_image():
    # Create a simple goat silhouette
    img = Image.new('RGB', (180, 280), '#34495E')
    draw = ImageDraw.Draw(img)
    
    # Goat body
    draw.ellipse([50, 100, 130, 160], fill='#95A5A6')
    
    # Head
    draw.ellipse([110, 70, 140, 100], fill='#95A5A6')
    
    # Legs
    draw.rectangle([60, 150, 70, 200], fill='#95A5A6')
    draw.rectangle([110, 150, 120, 200], fill='#95A5A6')
    
    return img

def save_images():
    # Create images directory if it doesn't exist
    if not os.path.exists('images'):
        os.makedirs('images')
    
    # Create and save images
    create_door_image().save('images/door_closed.png')
    create_car_image().save('images/car.png')
    create_goat_image().save('images/goat.png')

if __name__ == "__main__":
    save_images()