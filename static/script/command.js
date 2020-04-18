$(document).ready(() => {
  $('.toc__item').click(function() {
    var target = '#' + $(this).data('section');
    $(target).scroll();
  });
});
