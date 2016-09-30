for(i=0; i<100; i++) {
  $('.container').append('<div class="wave"></div>');
}

for(i=0; i<100; i++) {
  $('.container').append('<div class="drop"><div class="tail"></div><div class="head"></div></div>');
}

for(i=0; i<5; i++) {
  $('body').append('<div class="fish"><div class="head"></div><div class="body"></div><div class="tail"></div><div class="eye"></div></div>');
}


$('.drop').each( function() {
  $(this).css('left', (Math.random() * 100) + 1 + '%' );
  $(this).css('animation-duration', (Math.random()) + 1 + 's' );
  $(this).css('animation-delay', (Math.random() * 2) + 1 + 's' );
  $(this).css('opacity', Math.random());
  $(this).css('transform', 'scale('+Math.random()+')');
});

$('.wave').each( function() {
  $(this).css('left', (Math.random() * 100) - 5 + '%' );
  $(this).css('animation-duration', (Math.random()) + 1 + 's' );
});

$('.swash').each( function() {
  $(this).css('animation-duration', (Math.random()) + 0.25 + 's' );
});

$('.fish').each( function() {
  $(this).css('animation-duration', (Math.random()*100) + 30 + 's' );
  $(this).css('transform', 'scale('+Math.random()+')');
  $(this).css('opacity', Math.random());
  $(this).css('top', (Math.random() * 30) + 70 + '%' );
});

