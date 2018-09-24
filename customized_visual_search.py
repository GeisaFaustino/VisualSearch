from matplotlib import pyplot as plt
from urllib import request
import requests, json
import cv2
import http.client, urllib.parse
import json
import scipy.misc
import os
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.search.visualsearch import VisualSearchAPI
from azure.cognitiveservices.search.visualsearch.models import (
    VisualSearchRequest,
    CropArea,
    ImageInfo,
    Filters,
    KnowledgeRequest,
)


SUBSCRIPTION_KEY = 'ec53a1b526de4d33817227fb42045046'

DATA = 'C://Git//VisualSearch//data//'
BASE_URI = 'https://api.cognitive.microsoft.com/bing/v7.0/images/visualsearch'



"""
    Printing the object as json
"""
def print_json(obj):
    print(json.dumps(obj, sort_keys=True, indent=2, separators=(',', ': ')))
    
    
    
"""
    Printing a figure
"""    
def print_figure(img, fig_size=(8,8), fig_title=None):
    plt.figure(figsize=fig_size)
    if fig_title!=None:
        plt.title(fig_title, fontdict={'fontsize':20})
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    
    
    
"""
    Calculating top_left and bottom_right ounding box coordinates 
"""
def calculate_bounding_box_coordinates(float_top_left, float_bottom_right, shape):
    int_top_left = (int(shape[1]*float_top_left['x']),int(shape[0]*float_top_left['y']))
    int_bottom_right = (int(shape[1]*float_bottom_right['x']),int(shape[0]*float_bottom_right['y']))
    return(int_top_left, int_bottom_right)



"""
    Drawing bounding boxes
"""
def draw_bounding_boxes(img, visual_search_json, debug=False):
    img=img.copy()
    for element in visual_search_json['tags']:
        for actions in element['actions']:
            if actions['actionType'] == 'ProductVisualSearch' and 'boundingBox' in element:
                top_left, bottom_right = calculate_bounding_box_coordinates(element['boundingBox']['queryRectangle']['topLeft'],\
                                                       element['boundingBox']['queryRectangle']['bottomRight'],\
                                                       img.shape)
                cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)    
                print(element['displayName'])
                if debug:
                    print_json(element['boundingBox']['displayRectangle'])
                    print("\n")
    print_figure(img)
    
    
def draw_bounding_boxes(img, list_bounding_box, debug=False):
    img=img.copy()
    for bbox in list_bounding_box:
        cv2.rectangle(img, bbox[0], bbox[1], (0, 255, 0), 2)    
    print_figure(img)
    
    

"""
    Finding products in the image
"""   
def find_product_visual_search(img, visual_search_json, debug=False):
    products_visual_search = {}
    products_visual_search['productName'] = []
    products_visual_search['boundingBox'] = []
    for element in visual_search_json['tags']:
        for actions in element['actions']:
            if actions['actionType'] == 'ProductVisualSearch' and 'boundingBox' in element:
                products_visual_search['boundingBox']\
                    .append(calculate_bounding_box_coordinates(\
                        element['boundingBox']['queryRectangle']['topLeft'],\
                        element['boundingBox']['queryRectangle']['bottomRight'],\
                        img.shape)\
                    )
                products_visual_search['productName'].append(element['displayName'])
                if debug:
                    print_json(element['boundingBox']['displayRectangle'])
                    print("\n")
    return products_visual_search


    
"""
    Croping detected products from image
"""
def crop_image_products(img, products_visual_search, print_products = True):
    products_visual_search['croppedProduct'] = []
    for idx, ((top_left_x, top_left_y), (bottom_right_x, bottom_right_y)) in enumerate(products_visual_search['boundingBox']):
        img_product = img[top_left_y:bottom_right_y, top_left_x:bottom_right_x, :].copy()
        products_visual_search['croppedProduct'].append(img_product)
        if print_products:
            print_figure(img_product, fig_title=products_visual_search['productName'][idx])
    return products_visual_search
    

"""
    Printing detected products
"""
def print_detected_products_from_url(img_url, print_raw=True, print_bbox=True, print_products=True):
    #SAVING FILE
    file_path = DATA + 'input_image//' + 'temp.jpg'
    f = open(file_path, 'wb')
    f.write(request.urlopen(img_url).read())
    f.close()
    img = plt.imread(file_path)
    
    #API CALL
    HEADERS = {'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY}

    imagePath = file_path

    file = {'image' : ('myfile', open(file_path, 'rb'))}
    response = requests.post(BASE_URI, headers=HEADERS, files=file)
    response.raise_for_status()
    
    #EXTRACTING PRODUCTS FROM VISUAL SEARCH RESPONSE
    products = find_product_visual_search(img, response.json())
    if print_raw:
        print("Raw Image")
        print_figure(img)
    
    if print_bbox:
        print("Image w/ Bounding Box")
        draw_bounding_boxes(img, products['boundingBox'])
        
    products = crop_image_products(img, products, print_products)
    
    return products

"""
    Search similar images from input image using bing visual search
"""
def search( image_path, knowledge_request ):
    
    thumbnail_url_and_host_page_url = []

    # Instantiate the client
    client = VisualSearchAPI( CognitiveServicesCredentials(SUBSCRIPTION_KEY) )
       
    # Using the client to search images and parse results
    with open(image_path, "rb") as image_fd:

        # You need to pass the serialized form of the model
        knowledge_request = json.dumps( knowledge_request.serialize() )

        print("\r\nSearch visual search request with binary of input image")
        result = client.images.visual_search( image = image_fd, knowledge_request = knowledge_request )

        if not result:
            print("No visual search result data.")
            return

        # Visual Search results
        if result.image.image_insights_token:
            print("Uploaded image insights token: {}".format( result.image.image_insights_token ) )
        else:
            print("Couldn't find image insights token!")

        if result.tags:
            all_urls = result.tags[0].actions[2].data.value
            print( len(all_urls) )
            thumbnail_url_and_host_page_url = [(url.thumbnail_url, url.host_page_url) for url in all_urls]

    return  thumbnail_url_and_host_page_url


"""
    Searching for similar images from input image using bing visual search in a diven endpoint.
    The default endpoint (site) is www.bing.com
"""
def search_url_with_filter( image_path, site = "www.bing.com" ):

    filters = Filters( site = site )

    knowledge_request = VisualSearchRequest(
        knowledge_request = KnowledgeRequest( filters = filters )
    )
    return search( image_path, knowledge_request )


"""
    Saving images on disk in the given path
"""
def save_detected_products( images_list, path ):    
    
    # clean ditectory
    files = os.listdir(path)
    for f in files:
        os.remove(path + f)
    
    for i in range(len(images_list)):
        name = 'product_' + str(i) + '.png'
        output_path = path + name
        scipy.misc.imsave( output_path, images_list[i] )