import os


package_directory = os.path.dirname(os.path.abspath(__file__))
build_html_pages = os.path.join(package_directory, "_build/html/pages")
build_html_static = os.path.join(package_directory, "_build/html/_static")
build_html_source = os.path.join(package_directory, "_build/html/_sources")
build_html_images = os.path.join(package_directory, "_build/html/_images")
