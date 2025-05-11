document.addEventListener('DOMContentLoaded', function() {
  // Find instances of your name in page titles and headings
  const pageTitle = document.querySelector('.page__title');
  const authorName = document.querySelector('.author__name');
  const headings = document.querySelectorAll('h1, h2');
  
  // If there's both a page title and author name with your name, hide one
  if (pageTitle && authorName) {
    if (pageTitle.textContent.includes('Bhaskar Kumar') && 
        authorName.textContent.includes('Bhaskar Kumar')) {
      authorName.style.display = 'none';
    }
  }
  
  // Remove duplicate headings with your name
  let foundName = false;
  headings.forEach(heading => {
    if (heading.textContent.trim() === 'Bhaskar Kumar') {
      if (!foundName) {
        foundName = true;
      } else {
        heading.style.display = 'none';
      }
    }
  });
});
