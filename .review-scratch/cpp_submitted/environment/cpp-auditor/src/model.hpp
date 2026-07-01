#pragma once

#include <map>
#include <set>
#include <string>

struct Account {
    long uid = 0;
    bool disabled = false;
};

struct Normalized {
    std::map<std::string, Account> accounts;
    std::set<std::string> nopasswd_users;
    std::set<std::string> users_with_keys;
    std::map<std::string, std::string> sshd;  // lowercased key -> value
};
