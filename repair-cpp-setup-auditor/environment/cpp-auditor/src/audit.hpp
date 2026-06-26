#pragma once

#include <vector>

#include <nlohmann/json.hpp>

#include "model.hpp"

std::vector<nlohmann::json> run_audit(const Normalized& inv);
