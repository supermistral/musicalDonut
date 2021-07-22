const imageInitClickHandler = () => {
    const imagesWrappers = document.querySelectorAll(".img-cover img");
    if (imagesWrappers.length === 0) {
        return;
    }

    const wrapperContent = document.getElementById("content");
    
    imagesWrappers.forEach(item => {
        item.addEventListener('click', (e) => {
            document.body.className = "hidden";

            const imageSrc = e.target.src;
            const imageAlt = e.target.alt;

            let fullsizeWrapper = document.createElement('div');    
            fullsizeWrapper.className = "img-fullsize__wrapper";
            fullsizeWrapper.innerHTML = "<div class='img-fullsize__inner'>" +
                "<img src='" + imageSrc + "' alt='" + imageAlt + "'>" + 
                "<div class='cross'></div></div></div>";

            fullsizeWrapper.addEventListener('click', (e) => {
                const imgContainer = fullsizeWrapper.querySelector("img");
                if (e.target !== imgContainer) {
                    document.body.className = "";
                    fullsizeWrapper.remove();
                }
            });

            wrapperContent.append(fullsizeWrapper);
        });
    });
};

const sliderHandler = () => {
    const sliders = document.querySelectorAll('.img-cover.slider');
    if (sliders.length === 0) {
        return;
    }

    sliders.forEach(item => {
        const images = item.querySelectorAll('img');
        const imagesLength = images.length;
        let imageIndex = 0;

        const arrowPrev = item.querySelector('.prev');
        const arrowNext = item.querySelector('.next');
        let nodeCurNum = item.querySelector('.info span');

        const prevClick = () => {
            const imgCur = images[imageIndex];
            imageIndex = imageIndex > 0 ? imageIndex - 1 : imagesLength - 1;
            const imgNext = images[imageIndex];

            imgCur.className = "anim-right";
            imgNext.className = "active";
        };

        const nextClick = () => {
            const imgCur = images[imageIndex];
            imageIndex = imageIndex < imagesLength - 1 ? imageIndex + 1 : 0;
            const imgNext = images[imageIndex];

            imgCur.className = "anim-left";
            imgNext.className = "active";
        };

        const clickHandler = (callback) => {
            callback();
            nodeCurNum.textContent = imageIndex + 1;
        };

        const hm = new Hammer(item);
        hm.on("swipeleft", e => {
            clickHandler(nextClick);
        });
        hm.on("swiperight", e => {
            clickHandler(prevClick);
        });
        
        arrowPrev.addEventListener('click', () => {
            clickHandler(prevClick);
        });

        arrowNext.addEventListener('click', () => {
            clickHandler(nextClick);
        });
    })
};

const musicSliderHandler = () => {
    const musicRefs = document.querySelectorAll('.music-refs');
    const lengthOfStep = musicRefs[0].querySelector('.ref-item').offsetHeight;

    musicRefs.forEach(musicItem => {
        const refItems = musicItem.querySelectorAll('.ref-item');
        let musicSlider = musicItem.querySelector('.music-slider');
        // Начальный индекс массива рефов
        let currentIndex = 0;
        const topOffsetSlider = (refItems[0].offsetHeight - musicSlider.offsetHeight) / 2;

        const moveSlider = () => {
            const step = currentIndex * lengthOfStep + topOffsetSlider;
            musicSlider.style.transform = `translateY(${step}px)`;

            // Поставить актив картинке напротив
            for (let i = 0; i < refItems.length; ++i) {
                if (refItems[i].classList.contains("active")) {
                    refItems[i].classList.remove("active");
                }
            }
            refItems[currentIndex].classList.add("active");
        };

        refItems.forEach(item => {
            moveSlider();

            item.addEventListener('click', (e) => {
                if (e.target.tagName === "INPUT") {
                    currentIndex = e.target.id - 1;
                    moveSlider();
                }
            });
        });

        musicSlider.addEventListener('mousedown', e => {
            e.preventDefault();
            musicSlider.classList.add("active");

            const shiftY = e.clientY - musicSlider.getBoundingClientRect().top;
            const diffHeight = musicItem.offsetHeight - musicSlider.offsetHeight;

            const mouseMoveHandler = event => {
                let top = event.clientY - shiftY - musicItem.getBoundingClientRect().top;
                if (top < 0) {
                    top = 0;
                } else if (top > diffHeight) {
                    top = diffHeight;
                }

                musicSlider.style.transform = `translateY(${top}px)`;
            };

            const mouseUpHandler = event => {
                const translateY = +musicSlider.style.transform.replace(/[^\d.]/g, '');
                currentIndex = Math.trunc((translateY + lengthOfStep / 2) / lengthOfStep);     

                document.removeEventListener('mouseup', mouseUpHandler);
                document.removeEventListener('mousemove', mouseMoveHandler);

                musicSlider.classList.remove("active");
                moveSlider();
            };
            
            document.addEventListener('mousemove', mouseMoveHandler);
            document.addEventListener('mouseup', mouseUpHandler)
        });
        
        musicSlider.ondragstart = () => false;
    });
};

window.onload = () => {
    imageInitClickHandler();
    sliderHandler();
    musicSliderHandler();
};