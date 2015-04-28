function init()
{
    // init gray value slider
    GenericSlider.initSlider(
        slider = $( "#gray-slider" ),
        sliderInputs = $('input.gray'),
        0,
        255,
        0,
        255,
        function(values) {
            minGray = values[0] / 255;   
            maxGray = values[1] / 255;
            drawVolume(); 
        }
    );

}