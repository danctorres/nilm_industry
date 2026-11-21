#pragma once
#include <cctype>
#include <charconv>
#include <cmath>
#include <filesystem>
#include <format>
#include <fstream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "model.h"

namespace nilm {

inline std::string_view trim(std::string_view s) {
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front())) != 0) s.remove_prefix(1);
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back())) != 0) s.remove_suffix(1);
    return s;
}

inline double to_double(std::string_view s) {
    double v{};
    const auto [end, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
    if (ec != std::errc{} || end != s.data() + s.size() || !std::isfinite(v))
        throw std::runtime_error(std::format("bad number '{}'", s));
    return v;
}

struct Table {
    std::vector<std::string> header;
    std::vector<std::vector<std::string>> rows;

    [[nodiscard]] std::vector<std::string> text_column(std::size_t c) const {
        std::vector<std::string> out;
        out.reserve(rows.size());
        for (const auto& r : rows) out.push_back(r.at(c));
        return out;
    }
    [[nodiscard]] std::vector<double> column(std::size_t c) const {
        std::vector<double> out;
        out.reserve(rows.size());
        for (const auto& r : rows) out.push_back(to_double(r.at(c)));
        return out;
    }
};

// Comma separated, first row is the header, cells are trimmed, blank lines are skipped.
inline Table read_csv(const std::filesystem::path& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open " + path.string());
    Table t;
    std::size_t line_no = 0;
    for (std::string line; std::getline(in, line);) {
        ++line_no;
        if (trim(line).empty()) continue;
        std::vector<std::string> cells;
        for (std::size_t start = 0;;) {
            const auto comma = line.find(',', start);
            cells.emplace_back(trim(std::string_view(line).substr(start, comma - start)));
            if (comma == std::string::npos) break;
            start = comma + 1;
        }
        if (t.header.empty()) t.header = std::move(cells);
        else if (cells.size() != t.header.size())
            throw std::runtime_error(
                std::format("{}:{}: {} cells, header has {}", path.string(), line_no, cells.size(), t.header.size()));
        else t.rows.push_back(std::move(cells));
    }
    if (t.rows.empty()) throw std::runtime_error("no data rows in " + path.string());
    return t;
}

// Aggregate file: timestamp, active power[, more columns].
// States file: timestamp, then one 0/1 column per machine.
struct Dataset {
    std::vector<std::string> timestamps;
    std::vector<double> aggregate;
    std::vector<std::vector<int>> states;  // [sample][machine]

    [[nodiscard]] std::size_t size() const { return aggregate.size(); }
    [[nodiscard]] std::size_t machines() const { return states.empty() ? 0 : states.front().size(); }
    [[nodiscard]] Sample sample(std::size_t i) const { return {aggregate[i], states[i]}; }
};

inline Dataset load_dataset(const std::filesystem::path& aggregate_csv, const std::filesystem::path& states_csv) {
    const Table agg = read_csv(aggregate_csv);
    const Table st = read_csv(states_csv);
    if (agg.rows.size() != st.rows.size())
        throw std::runtime_error(std::format("{} has {} rows but {} has {}", aggregate_csv.string(), agg.rows.size(),
                                             states_csv.string(), st.rows.size()));
    if (agg.header.size() < 2)
        throw std::runtime_error("expected timestamp and active power columns in " + aggregate_csv.string());
    if (st.header.size() < 2)
        throw std::runtime_error("expected timestamp and one column per machine in " + states_csv.string());
    Dataset d{agg.text_column(0), agg.column(1), {}};
    if (d.timestamps != st.text_column(0))
        throw std::runtime_error(
            std::format("the timestamps of {} and {} differ", aggregate_csv.string(), states_csv.string()));
    for (const auto& row : st.rows) {
        std::vector<int> on;
        for (std::size_t c = 1; c < row.size(); ++c) on.push_back(to_double(row[c]) != 0.0 ? 1 : 0);
        d.states.push_back(std::move(on));
    }
    return d;
}

// Coefficient file: header, then one row of kCoefs values per machine.
inline std::vector<double> read_coefs(const std::filesystem::path& path) {
    std::vector<double> coefs;
    for (const auto& row : read_csv(path).rows) {
        if (row.size() != kCoefs)
            throw std::runtime_error(std::format("{}: expected {} coefficients per row", path.string(), kCoefs));
        for (const auto& cell : row) coefs.push_back(to_double(cell));
    }
    return coefs;
}

inline std::ofstream open_out(const std::filesystem::path& path) {
    if (path.has_parent_path()) std::filesystem::create_directories(path.parent_path());
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write " + path.string());
    return out;
}

inline void write_coefs(const std::filesystem::path& path, std::span<const double> coefs) {
    auto out = open_out(path);
    out << "Coef 0, Coef 1, Coef 2, Coef 3\n";
    for (std::size_t j = 0; j * kCoefs < coefs.size(); ++j) {
        const auto c = coefs_of(coefs, j);
        out << std::format("{}, {}, {}, {}\n", c[0], c[1], c[2], c[3]);
    }
}

inline void write_estimates(const std::filesystem::path& path, const Dataset& d,
                            std::span<const std::vector<double>> est /* [machine][sample] */) {
    auto out = open_out(path);
    out << "Timestamp, Aggregate_Active_Power";
    for (std::size_t j = 0; j < est.size(); ++j) out << std::format(", Estimate_{}", j);
    out << '\n';
    for (std::size_t i = 0; i < d.size(); ++i) {
        out << std::format("{}, {}", d.timestamps[i], d.aggregate[i]);
        for (const auto& e : est) out << std::format(", {}", e[i]);
        out << '\n';
    }
}

}  // namespace nilm
