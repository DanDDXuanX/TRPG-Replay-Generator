from PIL import Image

sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]

img = Image.open('./assets/icon.png')

resized_img = img.resize((256,256))

ico_filename = './assets/icon.ico'
resized_img.save(ico_filename, format='ICO',sizes=sizes)