import http.client, urllib.parse
import json
from azure.cognitiveservices.search.visualsearch import VisualSearchAPI
from azure.cognitiveservices.search.visualsearch.models import (
    VisualSearchRequest,
    CropArea,
    ImageInfo,
    Filters,
    KnowledgeRequest,
)
from msrest.authentication import CognitiveServicesCredentials


def search( image_path, subscription_key, knowledge_request ):
    
    thumbnail_url_and_host_page_url = []

    # Instantiate the client
    client = VisualSearchAPI( CognitiveServicesCredentials(subscription_key) )
       
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
            #for url in all_urls:
                #thumbnail_url_and_host_page_url.append( (url.thumbnail_url, url.host_page_url) )
                
    return  thumbnail_url_and_host_page_url



def cropped_image( image_path, subscription_key, top ,bottom ,left ,right ):
    
    crop_area = CropArea( top = top, bottom = bottom, left = left, right = right )
    knowledge_request = VisualSearchRequest( image_info = ImageInfo( crop_area = crop_area ) ) 
    
    return search( image_path, subscription_key, knowledge_request )



def binary_image( image_path, subscription_key ):
    
    knowledge_request = VisualSearchRequest()
    
    return search( image_path, subscription_key, knowledge_request )



def search_url_with_filter( image_path, subscription_key, image_url, site = "www.bing.com" ):

    filters = Filters( site = site )

    knowledge_request = VisualSearchRequest(
        image_info = ImageInfo( url = image_url ),
        knowledge_request = KnowledgeRequest( filters = filters )
    )

    return search( image_path, subscription_key, knowledge_request )
