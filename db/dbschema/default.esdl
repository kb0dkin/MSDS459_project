module default {
  type Guitar {
    required property type -> str;
    required property model -> str;
    
    property body_shape -> str;
    property pickups -> str;
    property no_strings -> int32;
    property scale_length -> float64;

    multi link ratings -> Review;
    
    link brand -> Manufacturer;
    link seller -> Vendor;
  }

  type Review {
    property normalized_rating -> float64; # value 0-1, so that it's consistent across platforms
    property written_review -> json; 
  }

  type Manufacturer {
    required property name -> str;
  }

  type Vendor {
    required property name -> str;
  }


}
