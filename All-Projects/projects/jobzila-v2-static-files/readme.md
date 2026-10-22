# Part 4 — Add Templates and Static Files

Now we will move from plain text to real HTML pages.

## Step 10. Create folders for templates and static files

Inside the same folder where `manage.py` exists, create:

```text
templates/
static/
```

Inside `static`, create:

```text
static/css/
static/scripts/
```

Your structure should look like this:

```text
myproject/
├── manage.py
├── templates/
└── static/
    ├── css/
    └── scripts/
```

---

## Step 11. Add CSS

Create:

```text
static/css/styles.css
```

Add:

```css
body {
    font-family: Arial, sans-serif;
    background-color: #f7f7f7;
    margin: 0;
}

header, footer {
    background-color: #ff8500;
    color: white;
    padding: 20px;
    text-align: center;
}

main {
    padding: 30px;
}

.card {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

a {
    color: #ff8500;
    text-decoration: none;
}
```

---

## Step 12. Add JavaScript

Create:

```text
static/scripts/myscript.js
```

Add:

```javascript
console.log("JobZila JavaScript loaded");
```

---