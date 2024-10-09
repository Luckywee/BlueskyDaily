import csv
from enum import Enum
import random
from atproto import Client, client_utils, models
from PIL import Image
import io

DATA_PATH = "/data/"
CSV_PATH = "/data_to_send.csv"

MAX_IMG_SIZE_KB = 900


# Set after

HASHTAGS = None
FILE_NAME = None
BLUESKY_HANDLE = None
BLUESKY_PASSWORD = None

def get_all_my_liked_posts(client : Client) -> list["Repost"]:
    params = models.AppBskyFeedGetActorLikes.Params(
        actor=BLUESKY_HANDLE,
        limit=100
    )
    response = client.app.bsky.feed.get_actor_likes(params)
    posts = []
    for feed_view in response.feed:
        post = feed_view.post

        cid = post.cid
        uri = post.uri
        text = post.record.text
        like = post.viewer.like

        repost = Repost()
        repost.cid = cid
        repost.uri = uri
        repost.text = text
        repost.like_uri = like

        posts.append(repost)
    
    return posts


def add_hashtags(text_builder : client_utils.TextBuilder):
    for tag in HASHTAGS:
        text_builder.tag("#" + tag, tag).text(" ")
    
    return text_builder

def get_image_bytes_from_path(image_path : str):
    with open(image_path, "rb") as file:
        image_bytes = file.read()
    
    image_size_kb = len(image_bytes) / 1024
    
    if image_size_kb > MAX_IMG_SIZE_KB:
        image_bytes = resize_image(image_path, image_size_kb)

    return image_bytes

import io
from PIL import Image

MAX_IMG_SIZE_KB = 900  # Target size in KB

def resize_image(image_path, image_size_kb):
    image = Image.open(image_path)

    # Initial scale factor based on the ratio of target size to the original size
    scale_factor = (MAX_IMG_SIZE_KB / image_size_kb) ** 0.5  # Square root for proportional scaling

    # Calculate new dimensions
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)

    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Save the resized image to a BytesIO object
    output_io = io.BytesIO()
    resized_image.save(output_io, format=image.format)  # Use the original format
    image_bytes = output_io.getvalue()

    final_size_kb = len(image_bytes) / 1024
    print(f"First resized image size: {final_size_kb} KB")

    # Fine-tuning: If the resized image is still too large, reduce the quality
    if final_size_kb > MAX_IMG_SIZE_KB:
        # Convert to JPEG and reduce quality if needed
        if resized_image.mode == 'RGBA':
            resized_image = resized_image.convert('RGB')  # Convert to RGB if necessary

        print(f"Image still too large, reducing quality...")
        quality = 100
        while final_size_kb > MAX_IMG_SIZE_KB and quality > 10:
            output_io = io.BytesIO()
            resized_image.save(output_io, format="JPEG", quality=quality)  # Save as JPEG
            image_bytes = output_io.getvalue()
            final_size_kb = len(image_bytes) / 1024
            print(f"Adjusted resized image size with quality {quality}: {final_size_kb} KB")
            quality -= 5  # Reduce quality incrementally

    return image_bytes


def update_csv_posted(img_id_to_update):
    file_path = f"./{FILE_NAME}{CSV_PATH}"
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.reader(csvfile, quotechar='"', skipinitialspace=True))

    for row in rows:
        if row[0] == img_id_to_update:
            row[3] = 1

    # Write back to CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

class TypeOfPost(Enum):
    IMAGE = 0
    REPOST = 1
    RANDOM = 2

class ImagePost:
    def __init__(self) -> None:
        self.id = ""
        self.text = ""
        self.image_paths: list[str] = []
        self.image_alts = []
        self.posted = False

    def __str__(self) -> str:
        return ", ".join(self.image_paths) + ": " + self.text

    def get_images_bytes(self):
        image_bytes_list = []
        for image_path in self.image_paths:
            full_image_path = "./" + FILE_NAME + DATA_PATH + image_path
            image_bytes_list.append(get_image_bytes_from_path(full_image_path))
        return image_bytes_list
        
    @staticmethod
    def create_from_csv(row: list[str]) -> "ImagePost":
        img_post = ImagePost()
        img_post.id = row[0]
        img_post.text = row[2].strip('"')

        img_post.image_paths = [img.strip() + ".png" for img in row[0].split('|')]
        img_post.image_alts = [alt.strip('"') for alt in row[1].split('|')]

        img_post.posted = bool(int(row[3]))

        return img_post
    
    def send_image(self, client : Client):
        text_builder = client_utils.TextBuilder()
        text_builder.text(self.text).text("\n\n")
        add_hashtags(text_builder)

        post = client.send_images(text_builder, self.get_images_bytes(), self.image_alts)

class Repost:
    def __init__(self) -> None:
        self.uri = ""
        self.cid = ""
        self.like_uri = ""
        self.text = ""
        self.reposted = False
    
    def send_repost(self, client : Client):
        client.repost(self.uri, self.cid)
    
    def repost(self, client : Client):
        client.repost(self.uri, self.cid)
        client.unlike(self.like_uri)


def do_random_action(client : Client, action_to_do):
    if action_to_do == TypeOfPost.RANDOM.value:
        choice_int = random.randint(0,1)
    else:
        choice_int = action_to_do

    if choice_int == 0: # Image
        images_to_do : list[ImagePost] = []
        with open("./" + FILE_NAME + CSV_PATH, newline='', encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile, quotechar='"', skipinitialspace=True)
            next(spamreader)
            for row in spamreader:
                img_post = ImagePost.create_from_csv(row)
                if not img_post.posted:
                    images_to_do.append(img_post)

        if len(images_to_do) == 0:
            return
        img_to_post = random.choice(images_to_do)
        print("Selected this post to be posted : " + str(img_to_post))

        img_to_post.send_image(client)

        update_csv_posted(img_to_post.id)

    else: # Repost
        posts = get_all_my_liked_posts(client)
        if len(posts) == 0:
            return

        post_to_repost = random.choice(posts)
        print("Selected this post to be reposted : " + post_to_repost.text)

        post_to_repost.repost(client)


def start_generic_posting(handle : str, password : str, file_data_name : str, hashtags : list[str], action_to_do : TypeOfPost = TypeOfPost.RANDOM):
    """
    Starts the process of posting an image or reposting to Bluesky.

    Args:
        handle (str): The Bluesky handle of the user.
        password (str): The Bluesky password of the user.
        file_data_name (str): The filename to retrieve data from.
        hashtags (list[str]): A list of hashtags to include in the post.
        action_to_do (TypeOfPost): The action to be performed (IMAGE, REPOST, or RANDOM).
    """
    global BLUESKY_HANDLE, BLUESKY_PASSWORD, FILE_NAME, HASHTAGS
    
    # Assign the received values to the global variables
    BLUESKY_HANDLE = handle
    BLUESKY_PASSWORD = password
    FILE_NAME = file_data_name
    HASHTAGS = hashtags

    client = Client()
    profile = client.login(handle, password)
    print('Welcome,', profile.display_name)

    do_random_action(client, action_to_do.value)

