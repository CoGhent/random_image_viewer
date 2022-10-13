# random_image_viewer

Random image viewer fetches IIIF manifests from the Linked Data Event Streams of five cultural heritage institutions: Huis van Alijn, Design Museum Gent, Industriemuseum, STAM and Archief Gent. It randomly selects one manifest and renders the image, title and institution on a webpage (see [view.py](https://github.com/CoGhent/random_image_viewer/blob/master/getimage/views.py)). With each refresh, a different random image from the Collections of Ghent is presented. To see this in action, click [here](https://cogent-random-image.herokuapp.com/).

This code is built using Django framework. To run this code, download the code, install django in a virtual environment (pipenv install django) and run 'python manage.py runserver' in the command line.

*for example*
![image](https://user-images.githubusercontent.com/78723853/192510703-3f9676de-6820-4b0b-b141-f3b1ccf002d4.png)
