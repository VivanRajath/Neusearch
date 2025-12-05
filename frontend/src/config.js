const config = {
    API_URL: process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://127.0.0.1:8000')
};

export default config;
