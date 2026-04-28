# Mumzworld Universal Category Taxonomy

This document outlines the foundation for the Category Intelligence Layer. To build a universal shopping copilot, we must move away from rigid 1-to-1 keyword matching and instead map semantic intents to a broader taxonomy.

## 1. The 6 Major Categories (Mock Scope)

We have selected 6 diverse categories to represent the full breadth of the Mumzworld platform for this prototype:

| Category | Primary Subcategories | Core User Intents |
| :--- | :--- | :--- |
| **Strollers & Gear** | Travel Systems, Lightweight Prams, Double Strollers | Mobility, commuting, jogging, travel. |
| **Car Seats** | Infant Carriers, Convertible Seats, Boosters | Safety, car travel, hospital discharge. |
| **Feeding** | Bottles, High Chairs, Breast Pumps, Sterilizers | Nutrition, colic, weaning, pumping at work. |
| **Nursery & Sleep** | Cribs, Bassinets, Sleep Sacks, Monitors | Sleep regression, room sharing, safety monitoring. |
| **Health & Pharmacy** | Thermometers, Nasal Aspirators, Vitamins | Illness, teething, hygiene, post-partum care. |
| **Travel & Outdoor** | Travel Cots, Carriers, Portable Changing Pads | Vacations, flights, outdoor excursions. |

## 2. Multi-Category Routing Logic

A true AI copilot must recognize when a mother's query spans multiple departments. 

### Examples of Semantic Multi-Category Mapping:
*   **Query:** *"My 6-month-old isn't sleeping well"*
    *   **Mapping:** `Nursery & Sleep` (sleep sacks, monitors), `Health & Pharmacy` (teething gel, humidifiers).
*   **Query:** *"Traveling with a toddler on a long flight"*
    *   **Mapping:** `Travel & Outdoor` (travel cots), `Strollers & Gear` (cabin-approved stroller), `Feeding` (snack cups).
*   **Query:** *"Going back to work soon, baby is 3 months"*
    *   **Mapping:** `Feeding` (breast pumps, bottles).
*   **Query:** *"Need something for colic"*
    *   **Mapping:** `Feeding` (anti-colic bottles), `Health & Pharmacy` (colic drops).

### Routing Heuristics
The Natural Language layer will map queries to categories using weighted keyword clustering rather than exact matches.
- `Sleep Cluster`: sleep, waking, tired, night, nap, crib, bed -> `Nursery`, `Health`
- `Travel Cluster`: flight, plane, trip, holiday, compact, cabin -> `Travel`, `Strollers`, `Car Seats`
- `Health Cluster`: sick, fever, crying, colic, teeth, rash -> `Health`, `Feeding`
- `Mobility Cluster`: walk, run, stairs, elevator, car, drive -> `Strollers`, `Car Seats`

This ensures that the retrieval layer provides the LLM with candidates from *all* relevant categories to synthesize a holistic recommendation.
