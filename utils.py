import json

import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import matplotlib.image as mpimg
import requests



def print_json(obj):
    """Print the object as json"""
    print(json.dumps(obj, sort_keys=True, indent=2, separators=(',', ': ')))
    
    
    
def rendering_input_image(image_path):
    image = mpimg.imread(image_path)
    plt.title('Input image')
    plt.imshow(image)
    plt.show()
    

    
def rendering_images_grid(m, n, images_data):
    f, axes = plt.subplots(m, n, figsize=(32,32))
    for i in range(m):
        for j in range(n):
            indice = i * n + j 
            if indice < len(images_data):
                img_data = images_data[ indice ]
                thumbnail_url = img_data[0]
                host_page_url = img_data[1]
                data = requests.get( thumbnail_url )
                data.raise_for_status()
                image = Image.open( BytesIO( data.content ) )
                axes[i][j].imshow( image )
                axes[i][j].axis( "off" )               
