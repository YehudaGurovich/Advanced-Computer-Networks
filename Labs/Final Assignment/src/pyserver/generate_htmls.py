from utils import open_json_file


CONTENT = open_json_file("messages.json")
STYLES = open_json_file("styles.json")


def generate_style_tag(styles: dict) -> str:
    """
    Generate the style tag for the HTML page
    """
    return f"""
    <style>
        body {{{styles.get('body', '')}}}
        .container {{{styles.get('container', '')}}}
        h1, h2 {{{styles.get('h1_h2', '')}}}
        p {{{styles.get('p', '')}}}
        ul {{{styles.get('ul', '')}}}
        li {{{styles.get('li', '')}}}
        strong {{{styles.get('strong', '')}}}
    </style>
    """


def generate_home_page() -> str:
    """
    Generate the response body for the home page
    """
    style_tag = generate_style_tag(STYLES)
    return f"""
    <html>
        <head>
            <title>Raven's Investigations</title>
            {style_tag}
        </head>
        <body>
            <div class="container">
                {CONTENT['welcome_message']}
                {CONTENT['about_section']}
                {CONTENT['services_offered']}
            </div>
        </body>
    </html>
    """


def generate_secret_mission_page() -> str:
    """
    Generate the response body for the secret mission page
    """
    style_tag = generate_style_tag(STYLES)
    return f"""
    <html>
        <head>
            <title>Secret Mission</title>
            {style_tag}
        </head>
        <body>
            <div class="container">
                {CONTENT['message']}
            </div>
        </body>
    </html>
    """


def generate_final_message_page() -> str:
    """
    Generate the response body for the final message page
    """
    style_tag = generate_style_tag(STYLES)
    return f"""
    <html>
        <head>
            <title>Final Message</title>
            {style_tag}
        </head>
        <body>
            <div class="container" style="padding-top: 20px;">
                {CONTENT['final_message']}
            </div>
        </body>
    </html>
    """


def add_secret_field() -> str:
    """
    Add the secret field to the response body
    """
    return CONTENT['curl_secret']
