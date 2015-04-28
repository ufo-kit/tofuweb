function init()
{
    // init gray value slider
    $('#gray_slider').slider()
    .on('slideStop', function(e) {
        minGray = e.value[0] / 255;   
        maxGray = e.value[1] / 255;
        drawVolume(); 

    });
    
}