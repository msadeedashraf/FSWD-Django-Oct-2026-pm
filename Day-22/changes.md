## Final JobZila Version 

[Final Code](../django-jobzila-projects/09-jobzila-crud-blog/jobzilav3/)

1. FIx the Blog CSS

```css

/* ========================================
   ADD AND EDIT BLOG FORM
   ======================================== */

.blog-form-section {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 40px 20px;
}

.blog-form-card {
    width: 100%;
    max-width: 750px;
    background: #fff;
    border: 1px solid #ccc;
    border-top: 5px solid #ff8500;
    border-radius: 5px;
    padding: 25px;
}

.blog-form-card h2 {
    margin-bottom: 5px;
    color: #333;
}

.blog-form-intro {
    margin-bottom: 25px;
    color: #666;
}

/* Works with Django form.as_p */

.blog-form p {
    margin-bottom: 18px;
}

.blog-form label {
    display: block;
    margin-bottom: 6px;
    font-weight: bold;
    color: #333;
}

.blog-form input,
.blog-form textarea,
.blog-form select {
    width: 100%;
    padding: 10px;
    margin-top: 4px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
}

.blog-form textarea {
    min-height: 180px;
    resize: vertical;
}

.blog-form input[type="file"] {
    padding: 8px;
}

.blog-form input[type="checkbox"] {
    width: auto;
    margin-right: 8px;
}

.blog-form input:focus,
.blog-form textarea:focus,
.blog-form select:focus {
    outline: none;
    border-color: #ff8500;
    box-shadow: 0 0 3px rgba(255, 133, 0, .35);
}

.blog-form .helptext {
    display: block;
    margin-top: 5px;
    color: #666;
    font-size: 14px;
}

.blog-form ul {
    margin: 6px 0 0 18px;
    color: #666;
    font-size: 14px;
}

.blog-form .errorlist {
    margin: 6px 0;
    padding: 10px;
    border: 1px solid #dc3545;
    border-radius: 3px;
    background: #fff5f5;
    color: #c62828;
    list-style-position: inside;
}

/* ========================================
   BLOG FORM BUTTONS
   ======================================== */

.blog-form-buttons {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 25px;
}

.blog-form button {
    padding: 10px 18px;
    border: none;
    border-radius: 3px;
    background: #333;
    color: white;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
    transition: .2s;
}

.blog-form button:hover {
    background: #ff8500;
}

.blog-form-buttons a {
    color: #d96f00;
    text-decoration: none;
    font-weight: bold;
}

.blog-form-buttons a:hover {
    text-decoration: underline;
}

/* ========================================
   EDIT AND DELETE BLOG
   ======================================== */

.blog-management-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
}

.edit-blog-link,
.delete-blog-link {
    display: inline-block;
    padding: 9px 15px;
    border-radius: 3px;
    text-decoration: none;
    font-weight: bold;
}

.edit-blog-link {
    background-color: #333;
    color: white;
}

.edit-blog-link:hover {
    background-color: #ff8500;
}

.delete-blog-link {
    border: 1px solid #c62828;
    background-color: white;
    color: #c62828;
}

.delete-blog-link:hover {
    background-color: #c62828;
    color: white;
}

.back-to-blogs {
    margin-top: 20px;
}

.back-to-blogs a {
    color: #d96f00;
    text-decoration: none;
}

.back-to-blogs a:hover {
    text-decoration: underline;
}

/* ========================================
   DELETE BLOG CONFIRMATION
   ======================================== */

.delete-blog-card {
    max-width: 600px;
}

.delete-blog-warning,
.blog-delete-warning {
    margin: 15px 0;
    padding: 12px;
    border: 1px solid #c62828;
    border-radius: 3px;
    background-color: #fff5f5;
    color: #a61b1b;
    font-weight: bold;
}

.delete-blog-information {
    margin-bottom: 15px;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 3px;
    background-color: #f8f8f8;
}

.delete-blog-information h3 {
    margin-bottom: 5px;
}

.delete-blog-form {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 25px;
}

.delete-blog-button,
.blog-form .delete-blog-button {
    padding: 10px 18px;
    border: none;
    border-radius: 3px;
    background-color: #c62828;
    color: white;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
}

.delete-blog-button:hover,
.blog-form .delete-blog-button:hover {
    background-color: #941c1c;
}

.delete-blog-form a {
    color: #d96f00;
    text-decoration: none;
}

.delete-blog-form a:hover {
    text-decoration: underline;
}

/* Blog article body */

.blog-body {
    line-height: 1.7;
    overflow-wrap: anywhere;
}

/* ========================================
   BLOG FORM MOBILE LAYOUT
   ======================================== */

@media screen and (max-width: 700px) {

    .blog-form-section {
        padding: 20px 15px;
    }

    .blog-form-card {
        padding: 20px;
    }

    .blog-form-buttons,
    .blog-management-actions,
    .delete-blog-form {
        flex-direction: column;
        align-items: stretch;
    }

    .blog-form-buttons button,
    .blog-form-buttons a,
    .edit-blog-link,
    .delete-blog-link,
    .delete-blog-button,
    .delete-blog-form a {
        width: 100%;
        text-align: center;
    }
}

```

2. Fix the Blog's details CSS

```css
/* ========================================
   BLOG DETAIL PAGE — IMAGE FIX
   ======================================== */

/* Blog detail image container */
.blog-detail-banner-wrap {
    width: 100%;
    max-width: 900px;
    margin: 20px auto;
    aspect-ratio: 16 / 9;
    overflow: hidden;
    border-radius: 5px;
    background-color: #f8f8f8;
}

/* Blog detail image */
.blog-detail-banner {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
}

/* Mobile layout */
@media screen and (max-width: 700px) {
    .blog-detail-banner-wrap {
        aspect-ratio: 4 / 3;
    }
}
```

1. Mark the area to change in blog_detail.html

```html

<!-- ========================================
     CHANGE THIS AREA: BLOG DETAIL IMAGE
     ======================================== -->

{% if blog.banner %}
    <div class="blog-detail-banner-wrap">
        <img
            class="blog-detail-banner"
            src="{{ blog.banner.url }}"
            alt="{{ blog.title }}"
        >
    </div>
{% endif %}

<!-- END OF BLOG DETAIL IMAGE CHANGE -->

```

3. Implement Session expiry

- Update jobzila project level settings.py

```py


# ==========================================
# SESSION SECURITY
# ==========================================

# Expire login after 10 minutes of inactivity
SESSION_COOKIE_AGE = 600

# Refresh session expiry on every request
SESSION_SAVE_EVERY_REQUEST = True

# Also expire the session when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


```

- Verify the session middleware, In the same settings.py, confirm that these entries exist:
- If it exist then leave it as it.

```py
INSTALLED_APPS = [
    # Existing apps...
    "django.contrib.sessions",
]
```


