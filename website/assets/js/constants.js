export const CSS_CLASSES = {
    popup: {
        fullscreen: "fullscreen-popup",
        targetNoClick: "no-click",
    },
};


export const BASE_URL = process.env.DEBUG === "1" ? "http://127.0.0.1:8000" 
    : process.env.SITE_URL;