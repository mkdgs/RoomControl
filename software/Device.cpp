#include "Device.hpp"
#include "util.hpp"


static const Device::State switchStates[] = {
	{"Off", Device::OFF},
	{"On", Device::ON}};

static const Device::Transition switchTransitions[] = {
	{Device::OFF, Device::ON},
	{Device::ON, Device::OFF}};
	
static const Device::State dimmerStates[] = {
	{"Off", Device::OFF},
	{"On", Device::ON},
	{"Value", Device::VALUE},
	{"Lighten", Device::LIGHTEN},
	{"Darken", Device::DARKEN},
	{"Dim", Device::DIM}, // dim into opposite direction as last dimming
	{"Stop", Device::STOP}};

static const Device::Transition dimmerTransitions[] = {
	{Device::DIM, Device::STOP},
	{Device::VALUE, Device::VALUE}};

static const Device::State blindStates[] = {
	{"Closed", Device::CLOSED}, // not needed as action because raise can be used
	{"Open", Device::OPEN}, // not needed as action because lower can be used
	{"Value", Device::VALUE},
	{"Raise", Device::RAISE},
	{"Lower", Device::LOWER},
	{"Move", Device::MOVE}, // move into opposite direction as last movement
	{"Stop", Device::STOP}};

static const Device::Transition blindTransitions[] = {
	{Device::MOVE, Device::STOP},
	{Device::VALUE, Device::VALUE}};

static const Device::State handleStates[] = {
	{"Locked", Device::LOCKED},
	{"Closed", Device::CLOSED},
	{"Open", Device::OPEN},
	{"Tilt", Device::TILT},
	{"Shut", Device::SHUT}, // closed or locked
	{"Unshut", Device::UNSHUT}, // open or tilt
	{"Unlocked", Device::UNLOCKED}}; // closed, open or tilt


Array<Device::State> Device::getStates() const {
	switch (this->type) {
	case Type::SWITCH:
	case Type::LIGHT:
		return switchStates;
	case Type::DIMMER:
		return dimmerStates;
	case Type::BLIND:
		return blindStates;
	case Type::HANDLE:
		return handleStates;
	}
}

Array<Device::State> Device::getActionStates() const {
	switch (this->type) {
	case Type::SWITCH:
	case Type::LIGHT:
		return switchStates;
	case Type::DIMMER:
		return dimmerStates;
	case Type::BLIND:
		return Array<Device::State>(blindStates + 2, size(blindStates) - 2);
	case Type::HANDLE:
		// handle is only a sensor, therefore no state can be set by an action
		return {};
	}
}

Array<Device::Transition> Device::getTransitions() const {
	switch (this->type) {
	case Type::SWITCH:
	case Type::LIGHT:
		return switchTransitions;
	case Device::Type::DIMMER:
		return dimmerTransitions;
	case Device::Type::BLIND:
		return blindTransitions;
	case Type::HANDLE:
		return {};
	}
}

String Device::getStateName(uint8_t state) const {
	for (const State &s : getStates()) {
		if (s.state == state)
			return string(s.name);
	}
	return {};
}
