import React, { Component } from "react";
import Bundle from "Components/common/bundle";

const lazy = (BundleComponent, LazyComponent) => {
    const LazyComponents = props => (
        <Bundle load={BundleComponent}>
            {(LazyComponent) => <LazyComponent {...props} />}
        </Bundle>
    );
    return LazyComponents;
};

export default lazy;