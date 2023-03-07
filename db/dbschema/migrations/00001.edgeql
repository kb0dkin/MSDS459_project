CREATE MIGRATION m1ljwtoyzk5knu6cu6nnjiuriaxlqvtmwancceapjstnocubyvueza
    ONTO initial
{
  CREATE FUTURE nonrecursive_access_policies;
  CREATE TYPE default::Manufacturer {
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::Vendor {
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::Guitar {
      CREATE LINK brand -> default::Manufacturer;
      CREATE MULTI LINK seller -> default::Vendor;
      CREATE PROPERTY body_shape -> std::str;
      CREATE PROPERTY country_of_origin -> std::str;
      CREATE PROPERTY cutaway -> std::str;
      CREATE PROPERTY description -> std::str;
      CREATE REQUIRED PROPERTY model -> std::str;
      CREATE PROPERTY num_frets -> std::int32;
      CREATE PROPERTY num_strings -> std::int32;
      CREATE PROPERTY pickups -> std::str;
      CREATE PROPERTY scale_length -> std::float64;
      CREATE REQUIRED PROPERTY type -> std::str;
  };
  CREATE SCALAR TYPE default::SourceType EXTENDING enum<Vendor, Independent>;
  CREATE TYPE default::ReviewSource {
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE PROPERTY sourceType -> default::SourceType;
  };
  CREATE TYPE default::Review {
      CREATE LINK guitar -> default::Guitar;
      CREATE LINK source -> default::ReviewSource;
      CREATE PROPERTY best_for -> array<std::str>;
      CREATE PROPERTY cons -> array<std::str>;
      CREATE PROPERTY date -> std::datetime;
      CREATE PROPERTY normalized_rating -> std::float64;
      CREATE PROPERTY pros -> array<std::str>;
      CREATE PROPERTY written_review -> std::str;
  };
  CREATE TYPE default::Reviewer {
      CREATE MULTI LINK review -> default::Review;
      CREATE MULTI LINK source -> default::ReviewSource;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
};
