const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');


const db = new sqlite3.Database('../backend/instance/users.db', (err) => {
  if (err) {
    return console.error('Failed to connect:', err.message);
  }
  console.log('Connected to the database.');
});

function insertData(name, major, year, classes, study_style){
    const db = new sqlite3.Database('../backend/instance/users.db')

    db.run(`INSERT INTO users (name, major, year, classes, study_style) VALUES (?, ?, ?, ?, ?)`, [name, major, year, classes, study_style], function(err) {
        if (err) {
            console.error(err.message);
        } else {
            console.log(`A row has been inserted with rowid ${this.lastID}`);
        }
    });
}

insertData("John Doe", "Computer Science", 4, "CS101 CS102", "Visual");
insertData("Jane Smith", "Mathematics", 3, "MATH101 MATH102", "Auditory");
insertData("Alice Johnson", "Physics", 2, "PHYS101 PHYS102", "Visual");

userid = 1
db.get('SELECT * FROM users WHERE id = ?', [userid], (err, row) => {
    if (err) {
        console.error("Error fetching user:", err.message);
    }

    let lines = fs.readFileSync('../frontend/profiledisplay.html', 'utf8').split('\n');

    lines[43] = `<h3>Name: ${row.name}</h3>`;
    lines[44] = `<h3>Email: abcdef@gmail.com</h3>`;
    lines[45] = `<h3>Major: ${row.major}</h3>`;
    lines[46] = `<h3>Year: ${row.year}</h3>`;
    lines[47] = `<h3>Classes: ${row.classes}</h3>`;
    console.log(row.classes)
    lines[48] = `<h3>Bio: ${row.study_style}</h3>`;
    
    fs.writeFileSync('../frontend/profiledisplay.html', lines.join("\n"));

    db.close();
});