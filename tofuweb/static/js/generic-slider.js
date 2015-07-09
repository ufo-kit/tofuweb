GenericSlider = {
    initSimpleSlider: function(sliderElement, inputElement, startVal, minVal, maxVal, callbackOnChange, callbackOnReposition) {
        var slider = sliderElement,
            sliderInput = inputElement;

        $(sliderInput).val(startVal);

        slider.slider(
            {
                min: minVal,
                max: maxVal,
                value: startVal,
                slide: function( event, ui ) {
                    var value = ui.value;

                    $(sliderInput).val(value);
                    callbackOnChange(value);
                }
            }
        );

        slider.on('reposition', function() {
            value = callbackOnReposition();
            slider.slider('value', value);
            $(sliderInput).val(value);
        });

        sliderInput.change(function(e) {
            e.preventDefault();
            e.stopPropagation();

            var value = $(sliderInput).val();

            if(value < minVal || value > maxVal) {
                $(sliderInput).val(slider.slider('value'));
                return;
            }

            slider.slider('value', value);
            callbackOnChange(value);
        });

    },

    initSlider: function(sliderElement, inputElements, minVal, maxVal, leftVal, rightVal, callbackOnChange, callbackOnReposition) {
        var slider = sliderElement,
            sliderInputs = inputElements;

        $(sliderInputs[0]).val(minVal);
        $(sliderInputs[1]).val(maxVal);

        slider.slider(
            {
                range: true,
                min: minVal,
                max: maxVal,
                values: [ leftVal, rightVal ],
                slide: function( event, ui ) {
                    var values = ui.values;

                    $(sliderInputs[0]).val(values[0]);
                    $(sliderInputs[1]).val(values[1]);
                    callbackOnChange(values);
                }
            }
        );

        slider.on('reposition', function() {
            values = callbackOnReposition();
            slider.slider('values', values);
            $(sliderInputs[0]).val(values[0]);
            $(sliderInputs[1]).val(values[1]);
        });

        sliderInputs.change(function(e) {
            e.preventDefault();
            e.stopPropagation();

            var curMin = $(sliderInputs[0]).val(),
                curMax = $(sliderInputs[1]).val(),
                values = [curMin, curMax];

            if(curMin < minVal) {
                $(sliderInputs[0]).val(slider.slider('values')[0]);
                return;
            }

            if(curMax > maxVal) {
                $(sliderInputs[1]).val(slider.slider('values')[1]);
                return;
            }

            slider.slider('values', values);
            callbackOnChange(values);
        });
    },

    setPosSlider: function(sliderElement, inputElements, leftVal, rightVal) {
        var slider = sliderElement,
            sliderInputs = inputElements;

        $(sliderInputs[0]).val(leftVal);
        $(sliderInputs[1]).val(rightVal);

        slider.slider(
            {
                range: true,
                values: [ leftVal, rightVal ],
            }
        );

    }
}
