# Wrec-API
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

Visualize your book consumption and reading biases using the dewey decimal system.

## Table of Contents
- [Quick Usage](#quick-usage)
- [Background](#background)
- [Install](#install)
- [Environment variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Quick Usage
1. Use `/login` endpoint and choose a login method. Then follow the url path to login into Goodreads. Make sure this is the method you normally use for logging in.
2. After logging in, the site will redirect you to the list of books that have been uploaded. To see them in different Dewey Decimal Levels, try out
- `/bookshelf/linear-bookshelf/level_1/user/{user_id}`
- `/bookshelf/linear-bookshelf/level_2/user/{user_id}`.

## Background
An API grouping all of a user's books from goodreads by the dewey decimal system. That way, it's easier to see which genres a user doesn't read. This is an attempt to find the gaps in our reading bubbles and reaad more broadly.

This is an example of seeing a user's books categorized by the Level 1 Dewey Decimal system (Level 1 has ten categories). This json gives us a good idea of the user's reading preferences, and would maybe be pushed to read something from the "Language" or "History & geography" category.

```
[
  {
    "books": [
      [
        {
          "author": "Matthew Desmond",
          "dewey_decimal": 339,
          "title": "Evicted: Poverty and Profit in the American City"
        },
        {
          "author": "Samuel I. Schwartz",
          "dewey_decimal": 388,
          "title": "Street Smart: The Rise of Cities and the Fall of Cars"
        },
        {
          "author": "Michael Pollan",
          "dewey_decimal": 394,
          "title": "The Omnivore's Dilemma: A Natural History of Four Meals"
        }
      ]
    ],
    "code": 300,
    "description": "Social sciences"
  },
  {
    "books": [
      []
    ],
    "code": 400,
    "description": "Language"
  },
  {
    "books": [
      [
        {
          "author": "Jon Krakauer",
          "dewey_decimal": 917,
          "title": "Into the Wild"
        }
      ]
    ],
    "code": 900,
    "description": "History & geography"
  }
]

```

The purpose of this project is to compare a user's book classifications to the total available classifications. One option for this is to use the Dewey Decimal System and nesting the three levels of categories:

```
Level 1: 10 categories
Level 2: 100 categories
Level 3: 1000 categories
```

API stack:
- Flask
- PostGreSQL - hosted on ElephantSQL
- Deployed - docker image on Render

This project was inspired by Neil Pasricha's blog post [8 More Ways To Read (A Lot) More Books](https://www.neil.blog/articles/8-more-ways-to-read-a-lot-more-books#yui_3_17_2_1_1687286122789_289) and partially by Morgan Housel's blog post [How to Read: Lots of Inputs and a Strong Filter ](https://collabfund.com/blog/how-to-read-lots-of-inputs-and-a-strong-filter/).

**Front end**: While this is only the API, the `/circle-packing` endpoint is meant to be used with this [D3 Zoomable Circle Packing Visualization](http://jeromefroe.github.io/circlepackeR/) library which makes it easy to show nested dewey decimal categories and a user's corresponding books by using this [JSON structure](https://gist.githubusercontent.com/mbostock/1093025/raw/05621a578a66fba4d2cbf5a77e2d1bb3a27ac3d4/flare.json). See [API Endpoints](#api-endpoints) section below to render a circle packing json.

I would love extend this idea to music and movies too!

## Install
### Docker
Run the dockerfile locally:

```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" IMAGE_NAME sh -c "flask run --host 0.0.0.0"
```

### Manual
1. You can either clone the project by running`git clone https://github.com/tas09009/Wrec-API.git` in your terminal or fork the project in order to contribute later: See [Contributing](#contributing) below.

1. Set up your Python virtual environment by running `pyvenv venv` in that directory and running `source venv/bin/activate` to active it. Or create a conda environment.
2. make sure `pip` is installed
3. Install Python requirements with `pip install -r requirements.txt`. You may need to install some [build prerequisites](https://www.psycopg.org/docs/install.html#build-prerequisites); on Debian-like systems, they include the packages `python3-dev` and `libpq-dev`. You can try running `pip install psycopg2-binary` first to see if that solves the issue.
4. Install PostgreSQL and create an empty database by running `createdb wrec` in your terminal
5. Create the models by running `flask db upgrade` in your terminal. The migration scripts in here will create three models of the dewey decimal levels.
7. At your terminal run `flask run`. Click on development server shown in your terminal [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

*Here are some files which you may find helpful when diving into the project:*
- `wrec-schema.jpg` - diagram of all the models
- `classify_api_flowchart.jpg` - This project utilizes the [Classify API](http://classify.oclc.org/classify2/api_docs/index.html) to convert ISBN values to their respective dewey decimal numbers. However, the process isn't straightforward as the API actually returns an XML document of that particular book's data. The XML is converted to JSON, then parsed to find the dewey number value. This process isn't standard hence, a flowchart of the algorithm needed to be created to clarify the steps. There are still some methods missing which need to be added to the flowchart. Here is a snippet of the flowchart:
![classify_api_snippet](./backend_flask/classify_api_snippet.jpg)

## Environment variables
Create a `.env` file at the project level by copying the `.env.example` file:
`cp .env.example .env`

## API Endpoints
Please reference this [Swagger documentation](https://wrec-api.onrender.com/swagger-ui).

## Contributing
Please follow along this excellent [step-by-step guide](https://www.dataschool.io/how-to-contribute-on-github/) to learn how to contribute to an open-source project

## License