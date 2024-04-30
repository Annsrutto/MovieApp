//TMDB

const API_KEY = 'api_key=928a86fa32cd492578b2921001b702a1';
const BASE_URL = 'https://api.themoviedb.org/3';
const API_URL = BASE_URL + '/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&'+API_KEY;

getMovies(API_URL);

function getMovies(url){

    fetch(url).then(res => res.json()).then(data => {

        showMovies(data);

    })
}