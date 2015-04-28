/*
	Copyright 2011 Vicomtech

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.
*/

#ifdef GL_ES
precision highp float;
#endif

varying vec4 frontColor;
varying vec4 pos;

uniform sampler2D uBackCoord;
uniform sampler2D uVolData;
uniform sampler2D uTransferFunction;

uniform float uNumberOfSlices;
uniform float uMinGray;
uniform float uMaxGray;
uniform float uSlicesOverX;
uniform float uSlicesOverY;
uniform float uSteps;

const float steps = 195.0;

float getVolumeValue(vec3 volpos)
{
	float s1,s2;
	float dx1,dy1;
	float dx2,dy2;

	vec2 texpos1,texpos2;

	s1 = floor(volpos.z*uNumberOfSlices);
	s2 = s1+1.0;

	dx1 = fract(s1/uSlicesOverX);
	dy1 = floor(s1/uSlicesOverY)/uSlicesOverY;

	dx2 = fract(s2/uSlicesOverX);
	dy2 = floor(s2/uSlicesOverY)/uSlicesOverY;
	
	texpos1.x = dx1+(volpos.x/uSlicesOverX);
	texpos1.y = dy1+(volpos.y/uSlicesOverY);

	texpos2.x = dx2+(volpos.x/uSlicesOverX);
	texpos2.y = dy2+(volpos.y/uSlicesOverY);

	return mix( texture2D(uVolData,texpos1).x, texture2D(uVolData,texpos2).x, (volpos.z*uNumberOfSlices)-s1);
}

void main(void)
{
	vec2 texC = pos.xy/pos.w;
	texC.x = 0.5*texC.x + 0.5;
	texC.y = 0.5*texC.y + 0.5;

	vec4 backColor = texture2D(uBackCoord,texC);

	vec3 dir = backColor.rgb - frontColor.rgb;
	vec4 vpos = frontColor;
  
  	float cont = 0.0;

	vec3 Step = dir/uSteps;

	vec4 accum = vec4(0, 0, 0, 0);
	vec4 sample = vec4(0.0, 0.0, 0.0, 0.0);
 	vec4 value = vec4(0, 0, 0, 0);

	float opacityFactor = 8.0;
	float lightFactor = 1.3;

	// const 999 - only how example big number
	// It because expression i < uSteps impossible
	for(float i = 0.0; i < 999.0; i+=1.0)
	{
	// It because expression i < uSteps impossible
		if(i == uSteps) {
			break;
		}

		vec2 tf_pos;

		tf_pos.x = getVolumeValue(vpos.xyz);
		tf_pos.y = 0.5;
		
		// value = texture2D(uTransferFunction,tf_pos);
		value = vec4(tf_pos.x);

		if(value.x < uMinGray || value.x > uMaxGray || value.a < 0.15) {
		    value = vec4(0.0);
		}

		// Process the volume sample
		sample.a = value.a * opacityFactor * (1.0/uSteps);
		sample.rgb = value.rgb * sample.a * lightFactor;
						
		accum.rgb += sample.rgb;
		accum.a += sample.a;

		//advance the current position
		vpos.xyz += Step;

		//break if the position is greater than <1, 1, 1>
		if(vpos.x > 1.0 || vpos.y > 1.0 || vpos.z > 1.0 || accum.a>=1.0)
			break;


	}

	gl_FragColor = accum;

}

