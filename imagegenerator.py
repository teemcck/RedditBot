import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

def get_offset(text, font):

    # Create a dummy image and draw the text to measure its bounding box
    dummy_image = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    
    # Calculate the offset based on the height of the text
    offset = (0, text_bbox[3] - text_bbox[1])
    
    return offset

def trim_transparent_border(image):
    """
    Trim transparent border around the image.
    """
    # Get the alpha channel of the image
    alpha = image.split()[3]

    # Get the bounding box of the non-transparent pixels
    bbox = alpha.getbbox()

    # If there is no bounding box (i.e., all pixels are transparent), return the original image
    if not bbox:
        return image

    # Trim the image to the bounding box
    trimmed_image = image.crop(bbox)

    return trimmed_image

def draw_subtitles(subtitles):
    for i, subtitle in enumerate(subtitles):
        # Determine the size of the text at a higher resolution
        font_size = 265
        upscaled_font = ImageFont.truetype("fonts/Invisible-ExtraBold.otf", font_size)
        dummy_image = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_image)
        text_bbox = draw.textbbox((0, 0), subtitle[0], font=upscaled_font)
        width = text_bbox[2] - text_bbox[0]
        height = text_bbox[3] - text_bbox[1]

        # Create an image with a transparent background at higher resolution
        image = Image.new('RGBA', (width + 50, height + 150), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Text position
        text_x = 25

        # offset upwards for smaller characters
        text_y = 75

        # Draw text with a black border
        border_size = 8  # Border size for better coverage
        # Generate a comprehensive set of offsets for smoother borders
        offsets = [
            (dx * border_size // 3 + 3, dy * border_size // 3 + 3)
            for dx in range(-3, 6)
            for dy in range(-3, 6)
            if dx != 0 or dy != 0
        ]

        for offset in offsets:
            draw.text((text_x + offset[0], text_y + offset[1]), subtitle[0], font=upscaled_font, fill="black")

        # Draw the text itself in white
        draw.text((text_x, text_y), subtitle[0], font=upscaled_font, fill="white")

        # Downscale image
        image = image.resize((int((width+50) * .35), int((height+150) * .35)), Image.LANCZOS)

        image = trim_transparent_border(image)

        # Save the image
        image_path = f"C:/Users/bigbr/Desktop/redditbot v2/temp/subtitles/subtitle{i}.png"
        image.save(image_path, "PNG", quality=95)

def calculate_text_dimensions(text, font, width=34):
    text_wrapper = textwrap.TextWrapper(width=width)
    lines = text_wrapper.wrap(text)
    line_height = font.getmetrics()[0]  # Get the height of a line

    # Strange height scaling fix... ?
    if len(lines) == 1:
        total_height = (line_height-3) * len(lines)
    elif len(lines) == 2:
        total_height = (line_height+2) * len(lines)
    elif len(lines) == 3:
        total_height = (line_height+5) * len(lines)
    elif len(lines) >= 4:
        total_height = (line_height+6) * len(lines)

    return total_height

def draw_title(title_text, upvotes, comments, subreddit):
    # Declare Constants
    TITLE_FONT_SIZE = 42
    TITLE_FONT_PATH = r"fonts/TommySoft.otf"
    SCALE_FACTOR = 6
    SHADOW_EXPANSION = 3  # Expansion size for the shadow to include the gradient

    # Load font
    title_text_font = ImageFont.truetype(TITLE_FONT_PATH, TITLE_FONT_SIZE)

    # Calculate text dimensions and image size at the original resolution
    height = calculate_text_dimensions(title_text, title_text_font)
    height += 230
    width = 825
    radius = int(height * 0.08)

    # Create background and shadow images at the original resolution
    background = np.ones((int(height * SCALE_FACTOR), int(width * SCALE_FACTOR), 3), dtype=np.uint8) * 255

    # Create the shadow at the original resolution
    shadow = np.ones((int(height), int(width), 3), dtype=np.uint8) * 10

    # Save shadow image
    background_path = "temp/images/title_background.png"
    shadow_path = "temp/images/background_shadow.png"
    cv2.imwrite(shadow_path, shadow)

    # Open shadow image
    shadow = Image.open(shadow_path)

    # Create a mask with rounded corners using anti-aliasing at the upscaled resolution
    mask = Image.new("L", (width * SCALE_FACTOR, height * SCALE_FACTOR), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([(0, 0), (width * SCALE_FACTOR, height * SCALE_FACTOR)], radius * SCALE_FACTOR, fill=255)

    # Apply the mask to the upscaled background
    background_rounded = Image.new("RGBA", (width * SCALE_FACTOR, height * SCALE_FACTOR))
    background_rounded.paste(Image.fromarray(background), (0, 0), mask=mask)

    # Downscale the background to the original resolution
    background_rounded = background_rounded.resize((width, height), Image.LANCZOS)

    # Create a larger shadow canvas to accommodate the gradient
    shadow_expanded_width = width + SHADOW_EXPANSION * 2
    shadow_expanded_height = height + SHADOW_EXPANSION * 2

    # Create shadow with Gaussian blur on a larger canvas
    shadow_rounded = Image.new("RGBA", (shadow_expanded_width * SCALE_FACTOR, shadow_expanded_height * SCALE_FACTOR))
    shadow_resized = shadow.resize((width * SCALE_FACTOR, height * SCALE_FACTOR), Image.LANCZOS)
    shadow_rounded.paste(shadow_resized, (SHADOW_EXPANSION * SCALE_FACTOR, SHADOW_EXPANSION * SCALE_FACTOR), mask=mask)
    shadow_rounded = shadow_rounded.filter(ImageFilter.GaussianBlur(radius=20))

    # Reduce shadow alpha for transparency
    shadow_r, shadow_g, shadow_b, shadow_a = shadow_rounded.split()
    shadow_a = shadow_a.point(lambda p: p * 180 / 255)
    shadow_rounded = Image.merge("RGBA", (shadow_r, shadow_g, shadow_b, shadow_a))

    # Downscale the shadow to the original resolution
    shadow_rounded = shadow_rounded.resize((shadow_expanded_width, shadow_expanded_height), Image.LANCZOS)

    # Save the shadow
    shadow_rounded.save(shadow_path, quality=95)

    # Add profile picture
    profile_picture_path = "saved_images/profilepic.jpg"
    profile_picture = Image.open(profile_picture_path)
    profile_picture_size = (77, 89)
    profile_picture_padding = (15, 13)
    resized_picture = profile_picture.resize(profile_picture_size)
    background_rounded.paste(resized_picture, profile_picture_padding)

    # Define additional padding
    additional_padding = len(upvotes) * 18

    # Add icons and logos
    tiktok_logo_path = "saved_images/tiktoklogo.png"
    verified_icon_path = "saved_images/verified.png"
    upvote_icon_path = "saved_images/upvoteicon.PNG"
    comment_icon_path = "saved_images/commenticon.PNG"

    add_icon(background_rounded, tiktok_logo_path, (60, 70), (736, 22))
    add_icon(background_rounded, verified_icon_path, (33, 33), (363, 33))
    add_icon(background_rounded, upvote_icon_path, (54, 57), (18, int(height) - 68))
    add_icon(background_rounded, comment_icon_path, (63, 57), (105 + additional_padding, int(height) - 65))

    # Add text
    add_text(background_rounded, upvotes, (75, int(height) - 63), (32, 32, 32), 39)
    add_text(background_rounded, comments, (168 + additional_padding, int(height) - 63), (32, 32, 32), 39)
    add_text(background_rounded, "boy_redditor", (114, 24), (32, 32, 32), 39)
    add_text(background_rounded, f"r/{subreddit}", (114, 65), (50, 50, 50), 30)
    add_wrapped_text(background_rounded, title_text, (27, 126), (32, 32, 32), title_text_font)

    # Create final background
    final_background = np.ones((int(height + 13), int(width + 12), 4), dtype=np.uint8) * 0
    final_background_path = "temp/images/final_background.png"
    cv2.imwrite(final_background_path, final_background)
    final_background = Image.open(final_background_path)

    # Overlay shadow and main background
    final_background.paste(shadow_rounded, (11 - SHADOW_EXPANSION, 12 - SHADOW_EXPANSION), shadow_rounded)
    final_background.paste(background_rounded, (0, 0), background_rounded)

    # Save the final image with higher quality
    final_background.save(background_path, quality=95)

    return background_path

def add_icon(image, icon_path, icon_size, icon_padding):
    icon = Image.open(icon_path)
    resized_icon = icon.resize(icon_size)
    image.paste(resized_icon, icon_padding)

def add_text(image, text, padding, color, font_size):
    font = ImageFont.truetype(r"fonts/TommySoft.otf", font_size)
    draw = ImageDraw.Draw(image)
    draw.text(xy=padding, text=text, font=font, fill=color)

def add_wrapped_text(image, text, padding, color, font):
    wrapper = textwrap.TextWrapper(width=34)
    wrapped_text = wrapper.wrap(text)
    draw = ImageDraw.Draw(image)
    y_text = padding[1]
    line_height = font.getbbox("hg")[3]  # Get the height of a line of text
    for line in wrapped_text:
        draw.text(xy=(padding[0], y_text), text=line, font=font, fill=color)
        y_text += line_height

# draw_subtitles(subtitles=(("first", "fasdfa"), ("a", "fasdfa"), ("Lg", "fasdfa"), ("Ha", "fasdfa")))
# draw_title(title_text="test", upvotes="20", comments="3", subreddit="testreddit")