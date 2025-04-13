const rejectButton = document.querySelector(".reject")
const tile = document.querySelector(".tile");
const acceptButton = document.querySelector(".accept");

function reloadText(){
    document.query
}

function createNewTile() {
    const newTile = document.createElement("div");

    newTile.classList.add("tile");

    newTile.innerHTML = 
        `<div class="tileinfo">
            <div class="tileinfofront">
                <h2 id="groupname">CSE12 McHenry</h2>
                <img id="tilepic" src="https://bora.co/wp-content/uploads/2015/12/bora_UCSC_McHenryLibrary_02.jpg">
            </div>
            <div class="tileinfoback">
                <h1>Info</h1>
                <h2>CSEXX Study Group</h2>
                <h2>Location: </h2>
                <h2>Time: </h2>
            </div>
        </div>
        <div class="buttons">
            <button class="reject"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Red_X.svg/2048px-Red_X.svg.png"></button>
            <button class="accept"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Green_check.svg/600px-Green_check.svg.png"></button>
        </div>
    `;

    

    tileBox = document.querySelector(".tilebox");
    tileBox.appendChild(newTile);
    newTile.style.transform = "translateY(800px)";

    setTimeout(() => { 
        newTile.style.transform = "translateY(0px)"; 
        newTile.style.transition = "transform 0.2s ease";
    }, 200);

    const newRejectButton = newTile.querySelector(".reject");
    const newAcceptButton = newTile.querySelector(".accept");


    newRejectButton.addEventListener("mouseleave", () => { 
        newRejectButton.style.transform = "none"; 
        newTile.style.transition = "transform 1s ease";
    });

    newAcceptButton.addEventListener("mouseleave", () => {
        newAcceptButton.style.transform = "none"; 
        newTile.style.transition = "transform 1s ease";
    });

    newRejectButton.addEventListener("click", () => {
        newTile.style.transform = "translateX(-300%)";
        newTile.style.transition = "transform 1s ease";
        setTimeout(() => {
            newTile.remove();
            createNewTile();
        }, 500);
    });

    newAcceptButton.addEventListener("click", () => {
        newTile.style.transform = "translateX(300%)";
        newTile.style.transition = "transform 1s ease";
        setTimeout(() => {
            newTile.remove();
            createNewTile();
        }, 500);
    });

    newTile.addEventListener('mouseleave', () => {
        newTile.style.transform = 'none';
    });
}

// rejectButton.addEventListener("mouseenter", () => {
//     tile.style.transform = "rotate(-0.05turn) ";
//     tile.style.transition = "transform 1s ease";
// });

tile.addEventListener('mouseleave', () => {
    tile.style.transform = 'none';
});

rejectButton.addEventListener("click", () => {
    tile.style.transform = "translateX(-300%)";
    tile.style.transition = "transform 1s ease";
    setTimeout(() => {
        tile.remove();
        createNewTile();
    }, 500);
});

// acceptButton.addEventListener("mouseenter", () => {
//     tile.style.transform = "rotate(0.05turn) ";
//     tile.style.transition = "transform 1s ease";
// });


acceptButton.addEventListener("click", () => {
    tile.style.transform = "translateX(300%)";
    tile.style.transition = "transform 1s ease";
    setTimeout(() => {
        tile.remove();
        createNewTile();
    }, 500);
});

// my groups button

document.getElementById('mygroups').addEventListener('click', () => {
    window.location.href = 'myGroups.html'; // Redirect to myGroups.html in the same tab
});

// profile button

document.getElementById('profile').addEventListener('click', () => {
    window.location.href = 'profiledisplay.html'; // Redirect to profiledisplay.html in the same tab
});