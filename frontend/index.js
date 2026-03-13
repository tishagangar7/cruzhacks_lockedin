const rejectButton = document.querySelector(".reject")
const tile = document.querySelector(".tile");
const acceptButton = document.querySelector(".accept");
const LOCAL_SWIPE_APPTS_KEY = "swiped_right_appointments";

function reloadText(){
    document.query
}
var count = 0;

picsList = ["/tilepics/baskin.jpg", "/tilepics/mchenry.jpg", "/tilepics/mchenry1.jpeg", "/tilepics/sne.jpg", "/tilepics/spaces-mchenry.jpg"]

classesList = ["CS101", "BIO20", "MATH23", "PHYS2B", "HIST10", "CHEM1A", "STAT5", "PHIL3", "ECON100A"]

places = ["McHenry", "Baskin", "SNE", "Digital Innovation Area", "Cowell Library"]

times = ["Morning", "Afternoon", "Evening", "Night", "Anytime (Open)"]

function saveSwipeAppointment(className, placeName, timeName) {
    let existing = [];
    try {
        existing = JSON.parse(localStorage.getItem(LOCAL_SWIPE_APPTS_KEY) || "[]");
        if (!Array.isArray(existing)) existing = [];
    } catch {
        existing = [];
    }
    existing.unshift({
        class_name: className,
        location: placeName,
        time_block: timeName,
        created_at: new Date().toISOString(),
    });
    localStorage.setItem(LOCAL_SWIPE_APPTS_KEY, JSON.stringify(existing));
}

function createNewTile() {
    const newTile = document.createElement("div");

    newTile.classList.add("tile");

    const tilePic = picsList[Math.floor(Math.random() * picsList.length)];
    const className = classesList[Math.floor(Math.random() * classesList.length)];
    const placeName = places[Math.floor(Math.random() * places.length)];
    const timeName = times[Math.floor(Math.random() * times.length)];

    newTile.innerHTML = 
        `<div class="tileinfo">
            <div class="tileinfofront">
                <h2 id="groupname">${className}</h2>
                <img id="tilepic" src="${tilePic}" alt="Study location">
            </div>
            <div class="tileinfoback">
                <h1>Info</h1>
                <h2>CSEXX Study Group</h2>
                <h2>Location: </h2>
                <h2>Time: </h2>
            </div>
        </div>
        <div class="buttons">
            <button class="reject" aria-label="Reject group"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Red_X.svg/2048px-Red_X.svg.png" alt="Reject"></button>
            <button class="accept" aria-label="Accept group"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Green_check.svg/600px-Green_check.svg.png" alt="Accept"></button>
        </div>
    `;

    classInfo = document.querySelector(".info");
    classInfo.innerHTML = 
    `
        <h1>${className} Study Group</h1>
        <h3>Information: ${className} Weeks 1 and 2</h1>
        <h3>Location: ${placeName}</h3>
        <h3>Time: ${timeName}</h3>

            
        <div id="filtersbox">
            <button id="filters" type="button" onclick="window.location.href='filters.html'">Filters</button>
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
        saveSwipeAppointment(className, placeName, timeName);
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
    const className = (document.querySelector(".info h1")?.textContent || "Study Group").replace(" Study Group", "").trim();
    const locationLine = document.querySelectorAll(".info h3")[1]?.textContent || "";
    const timeLine = document.querySelectorAll(".info h3")[2]?.textContent || "";
    const placeName = locationLine.replace("Location:", "").trim() || "Remote";
    const timeName = timeLine.replace("Time:", "").trim() || "Flexible";
    saveSwipeAppointment(className, placeName, timeName);
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