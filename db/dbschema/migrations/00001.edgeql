CREATE MIGRATION m1paghr6vk32ump5knam2ndhivwkzoonegik6fvzbzfe7dxsubypdq
    ONTO initial
{
  CREATE FUTURE nonrecursive_access_policies;
  CREATE TYPE default::Manufacturer {
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::Review {
      CREATE PROPERTY normalized_rating -> std::float64;
      CREATE PROPERTY written_review -> std::json;
  };
  CREATE TYPE default::Vendor {
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::Guitar {
      CREATE LINK brand -> default::Manufacturer;
      CREATE MULTI LINK ratings -> default::Review;
      CREATE LINK seller -> default::Vendor;
      CREATE PROPERTY body_shape -> std::str;
      CREATE REQUIRED PROPERTY model -> std::str;
      CREATE PROPERTY no_strings -> std::int32;
      CREATE PROPERTY pickups -> std::str;
      CREATE PROPERTY scale_length -> std::float64;
      CREATE REQUIRED PROPERTY type -> std::str;
  };
};
