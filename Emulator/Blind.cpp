#include "Blind.hpp"
#include <iostream>
#include <cmath>


Blind::Blind()
	: Widget(
		"#version 330\n"
		"uniform float value;\n"
		"in vec2 xy;\n"
		"out vec4 pixel;\n"
		"void main() {\n"
			"float f = fract((xy.y - value) * 20) * 1.5;"
			"float g = f < 1.0 ? f : (1.5 - f) * 2;"
			"float blind = g * 0.5 + 0.1;"
			"pixel = xy.y < value ? vec4(0.8, 0.8, 0.8, 1) : vec4(blind, blind, blind, 1);\n"
		"}\n")
{
	// get uniform locations
	this->valueLocation = getUniformLocation("value");	
}

Blind::~Blind() {
}

void Blind::setState() {
	// set uniforms
	glUniform1f(this->valueLocation, float(this->value) / (100.0f /* * 65536.0f*/));
}
