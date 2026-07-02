#pragma once

#include <nlohmann/json.hpp>

#include "model.hpp"

Normalized parse_snapshot(const nlohmann::json& body);
