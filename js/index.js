function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
  }

  // Slideshow Script
  let slideIndex = 0;
  function showSlides() {
    let slides = document.getElementsByClassName("mySlides");
    for (let i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) { slideIndex = 1 }
    slides[slideIndex - 1].style.display = "block";
    setTimeout(showSlides, 2000); // Change image every 2 seconds
  }

  // Modal Script
  function closeModal() {
    document.getElementById("myModal").style.display = "none";
  }
  
  window.onload = showSlides;

  // Scroll-to-Top Button
  const scrollToTopBtn = document.getElementById('scroll-to-top');
  window.onscroll = () => {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
      scrollToTopBtn.style.display = 'block';
    } else {
      scrollToTopBtn.style.display = 'none';
    }
  };
  scrollToTopBtn.onclick = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };