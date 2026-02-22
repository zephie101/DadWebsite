// Section toggle — .section-preview (simple)
document.querySelectorAll('.section-preview').forEach(function (preview) {
    preview.addEventListener('click', function () {
        var content = preview.nextElementSibling;
        content.classList.toggle('active');
    });
});

// Section toggle — .section-toggle (with ARIA)
document.querySelectorAll('.section-toggle').forEach(function (button) {
    button.addEventListener('click', function () {
        var content = button.nextElementSibling;
        var isExpanded = button.getAttribute('aria-expanded') === 'true';
        button.setAttribute('aria-expanded', !isExpanded);
        content.setAttribute('aria-hidden', isExpanded);
        content.classList.toggle('active', !isExpanded);
    });
});
