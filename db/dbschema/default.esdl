module default {
  scalar type SourceType extending enum<Vendor, Independent>;
  
  type Guitar {
    required property type -> str; # acoustic, electric, acoustic/electric?
    required property model -> str {
        constraint exclusive;
    };

    # properties about the guitar 
    property body_shape -> str;
    property cutaway -> str;
    property pickups -> str;
    property num_strings -> int32;
    property scale_length -> float64;
    property num_frets -> int32;
    property country_of_origin -> str;
    property description -> str;

    property pros -> array<str>; # pros
    property cons -> array<str>; # cons
    property best_for -> array<str>; # what is the guitar best for?

    # links to other types
    # multi link ratings -> Review;
    link brand -> Manufacturer;
    multi link seller -> Vendor {
        property url -> str;
        property price -> float64;
    }
  }

  type Review {
    property normalized_rating -> float64; # value 0-1, so that it's consistent across platforms
    property date -> datetime;  # when did we get the review?

    link guitar -> Guitar; # link it to a single guitar
    link source -> ReviewSource; # guitarCenter, GuitarWorld, other?

    property written_review -> str; # full written review, if applicable. For later NLP
  }

  type Manufacturer {
    required property name -> str {
        constraint exclusive;
    }; # who makes it?
  }

  type Vendor {
    required property name -> str {
        constraint exclusive;
    }; # who sells it? Probably only going to be populated for GC
  }

  type Reviewer { # this way we can see how they review different guitars
    required property name -> str{
      constraint exclusive;
    };

    multi link review -> Review; # link to their reviews
    multi link source -> ReviewSource; # where were they reviewing? Unlikely we can link across platforms, but...
  }


  type ReviewSource {
    required property name -> str {
        constraint exclusive;
    }; # GuitarCenter, GuitarWorld

    property sourceType -> SourceType; # Vendor or Independent (magazine etc)
  }

  # define acceptable source types -- vendor or independent
}


