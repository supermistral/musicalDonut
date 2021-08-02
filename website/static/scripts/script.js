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
    // Список всех песен
    const songRefs = document.querySelectorAll('.song__refs');
    if (songRefs.length === 0)
        return;

    // элемент с настройкой ссылок песни
    let musicItem = document.querySelector('.music-refs');

    const refItems = musicItem.querySelectorAll('.ref-item');
    if (refItems.length === 0) 
        return;

    const lengthOfStep = refItems[0].offsetHeight;
        
    // Слайдер
    let musicSlider = musicItem.querySelector('.music-slider');
    let musicRefsIndex = {
        firstIndex: 0,
        lastIndex: refItems.length - 1,
        indicesOfVisible: Array.from(Array(refItems.length), (v, k) => k),
        updateFirstIndex: function(newIndex) {
            if (newIndex === null) {
                return;
            }
            refItems[this.firstIndex].classList.remove('first');
            this.firstIndex = newIndex;
            refItems[this.firstIndex].classList.add('first');
        },
        updateLastIndex: function(newIndex) {
            if (newIndex === null) {
                return;
            }
            refItems[this.lastIndex].classList.remove('last');
            this.lastIndex = newIndex;
            refItems[this.lastIndex].classList.add('last');
        },
    };

    // Начальный индекс массива рефов и соответствующий сервис
    let currentService = localStorage.getItem('musicService') || 'apple';
    let currentIndex = (() => {
        for (let i = 0; i < refItems.length; ++i) {
            if (refItems[i].dataset.service === currentService) {
                return i;
            }
        }
        return 0;
    })();

    const setMusicService = (service) => {
        localStorage.setItem('musicService', service);
    }
    
    const setActiveSongs = (service) => {
        songRefs.forEach(songRef => {
            const songContainer = songRef.querySelector('.song__container');

            let activeSongBefore = null;
            for (let el of songContainer.children) {
                if (el.classList.contains('active')) {
                    el.classList.remove("active");
                    activeSongBefore = el;
                }
            }

            const song = songContainer.querySelector(`div[data-service=${service}]`);
            if (song) {
                song.classList.add('active');
            } else if (activeSongBefore !== null) {
                activeSongBefore.classList.add('active');
            } else {
                songContainer.children[0].classList.add('active');
            }
        });
    }

    // разница для корректного перемещения слайдера между блоками
    const topOffsetSlider = (refItems[musicRefsIndex.firstIndex].offsetHeight - musicSlider.offsetHeight) / 2;

    const moveSlider = (setActiveFlag = true) => {
        const step = musicRefsIndex.indicesOfVisible[currentIndex] * lengthOfStep + topOffsetSlider;
        musicSlider.style.transform = `translateY(${step}px)`;

        refItems[currentIndex].querySelector('input').checked = true;

        if (setActiveFlag) {
            const currentService = refItems[currentIndex].dataset.service; 
            setActiveSongs(currentService);
            setMusicService(currentService);
        }
    };

    refItems.forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.tagName === "INPUT") {
                const targetId = +e.target.id.replace(/[^\d]/g, '');
                currentIndex = targetId - 1;

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
            const indexOfVisible = Math.trunc((translateY + lengthOfStep / 2) / lengthOfStep);
            currentIndex = musicRefsIndex.indicesOfVisible.indexOf(indexOfVisible);

            document.removeEventListener('mouseup', mouseUpHandler);
            document.removeEventListener('mousemove', mouseMoveHandler);

            musicSlider.classList.remove("active");
            moveSlider(false);
        };
        
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler)
    });
    
    musicSlider.ondragstart = () => false;

    songRefs.forEach(songItem => {
        // элемент с песней / плейлистом
        const songContainer = songItem.querySelector('.song__container');
        // блок настроек для отображения слайдера
        const songInfo = songItem.querySelector('.song__info');

        const showMusicSlider = () => {
            const mouseEnterHandler = event => {
                event.preventDefault();
                
                const songWidgets = Array.from(songContainer.children);
                musicRefsIndex.indicesOfVisible.fill(null);
                
                let firstIndex = null;
                let lastIndex = 0;
                let counterVisible = 0;

                for (let i = 0; i < refItems.length; ++i) {
                    let ref = refItems[i];

                    if (!songWidgets.find(el => el.dataset.service === ref.dataset.service)) {
                        ref.classList.add('hidden');
                    } else {
                        if (ref.classList.contains('hidden')) {
                            ref.classList.remove('hidden');
                        }
                        if (firstIndex === null) {
                            firstIndex = i;
                        }
                        lastIndex = i;
                        musicRefsIndex.indicesOfVisible[i] = counterVisible++;
                    }
                }

                musicRefsIndex.updateFirstIndex(firstIndex);
                musicRefsIndex.updateLastIndex(lastIndex);

                if (musicRefsIndex.indicesOfVisible[currentIndex] === null) {
                    currentIndex = firstIndex;
                }

                // Начальная инициализаця
                moveSlider(false);

                songInfo.append(musicItem);

                setTimeout(() => {
                    musicItem.classList.add('active');
                }, 0); 
            };

            const mouseLeaveHandler = event => {
                musicItem.classList.remove('active');
            };

            songInfo.addEventListener('mouseenter', mouseEnterHandler);
            songInfo.addEventListener('mouseleave', mouseLeaveHandler);
        };

        showMusicSlider();
    });

    setActiveSongs(currentService);
};

const searchFormClickHandler = () => {
    const searchForm = document.querySelector('.search-form form');
    if (searchForm) {
        const input = searchForm.querySelector('input');
        searchForm.querySelector('span').addEventListener('click', e => {
            input.focus();
        });

        const button = searchForm.querySelector('button');
        const isEmptyInput = el => {
            const value = el.value.trim().length;
            button.disabled = value === 0;
        };

        input.addEventListener('keyup', e => {
            isEmptyInput(e.target);
        });

        isEmptyInput(input);
    }
};

window.onload = () => {
    searchFormClickHandler();
    imageInitClickHandler();
    sliderHandler();
    musicSliderHandler();
};