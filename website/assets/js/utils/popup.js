import { CSS_CLASSES } from "../constants";
import { translateClassObjToSelectors } from "./helpers";

const POPUP_CSS_CLASSES = translateClassObjToSelectors(CSS_CLASSES.popup);


export const isPopupWrapperClicked = (el) => {
    while (
        !el.classList.contains(CSS_CLASSES.popup.fullscreen) && 
        !el.classList.contains(CSS_CLASSES.popup.targetNoClick) &&
        (el = el.parentElement)
    );
    return el.classList.contains(CSS_CLASSES.popup.fullscreen);
};


export const popupClickHandler = (item, callback = null, time = 0) => {
    document.body.classList.add("hidden");

    const fullscreenPopup = item.querySelector(POPUP_CSS_CLASSES.fullscreen) || item;
    
    fullscreenPopup.addEventListener('click', e => {
        if (isPopupWrapperClicked(e.target)) {
            callback && callback();

            setTimeout(() => {
                fullscreenPopup.remove();
                document.body.classList.remove('hidden');
            }, time);
        }
    });
};