import PropTypes from 'prop-types';
import React from 'react';
import BaseChooser from './BaseChooser';

class FilterSelector extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      filterGroups: [],
      loading: true,
    };

    this.getFilterGroup = this.getFilterGroup.bind(this);
    this.loadFilters = this.loadFilters.bind(this);
    this.selectOption = this.selectOption.bind(this);
    this.getFilterParams = this.getFilterParams.bind(this);
    this.getCurrentFilterType = this.getCurrentFilterType.bind(this);
  }

  componentDidMount() {
    this.loadFilters();
  }

  loadFilters() {
    const { adjustable_filter_type } = this.props;
    const { filters_endpoint: url } = this.props;
    fetch(url, {
      credentials: 'same-origin',
    })
      .then(res => res.json())
      .then((json) => {
        if (adjustable_filter_type) {
          json.unshift({
            "label": "filter type",
            "name": "filter_type",
            "options": [
              {"label": "Exclusive", value: "exclusive", "selected": true},
              {"label": "Additive", value: "additive", "selected": false}
            ]
          })
        }
        this.setState({
          filterGroups: json,
          loading: false,
        });
      });
  };

  getCurrentFilterType() {
    const filterGroup = this.state.filterGroups.find((filterGroup) => filterGroup.name === "filter_type");
    if (!!filterGroup) {
      return filterGroup.options.find((option) => option.selected).value;
    }
    return "exclusive";
  }

  selectOption(selectedFilterGroup, selectedOption) {
    const currentFilterType = this.getCurrentFilterType();

    const newFilterGroup = Object.assign({}, selectedFilterGroup);
    const newOptions = newFilterGroup.options.map((option) => {
      const newOption = Object.assign({}, option);
      if (option.value === selectedOption.value) {
        newOption.selected = true;
      } else if (
        currentFilterType === "exclusive" || !selectedOption.value || !option.value || selectedFilterGroup.name === "filter_type") {
        newOption.selected = false;
      }
      return newOption;
    });
    newFilterGroup.options = newOptions;

    const newGroups = this.state.filterGroups.map((filterGroup) => {
      if (filterGroup.name === selectedFilterGroup.name) {
        return newFilterGroup;
      } else {
        return filterGroup;
      }
    });
    this.setState({
      filterGroups: newGroups
    }, () => {
      const { onFilterChanged } = this.props;
      onFilterChanged(this.getFilterParams());
    });

  }

  getFilterParams() {
    let queryString = "";
    this.state.filterGroups.map((filterGroup) => {
      const selectedOptions = filterGroup.options.filter((option) => option.selected);
      selectedOptions.map((selectedOption) => {
        if (!!selectedOption.value) {
          if (queryString.length > 0) {
            queryString += "&"
          }
          queryString += encodeURIComponent(filterGroup.name) + "=" + selectedOption.value;
        }
      });
    });

    return queryString;
  }

  getFilterGroup(filterGroup) {
    const { options } = filterGroup;

    return (
      <div className="admin-modal__filters_group">
        <p>By { filterGroup.label }</p>
        <ul>
          {options.map((option) => {
            return (
              <li className={ option.selected ? "selected" : "" }>
                <a onClick={() => this.selectOption(filterGroup, option)}>{ option.label }</a>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }

  render() {
    let content;
    if (this.state.loading) {
      content = (<p>Loading...</p>);
    } else {
      const { filterGroups } = this.state;
      if (filterGroups.length === 0) {
        return (null);
      }

      content = filterGroups.map((filterGroup) => {
        return this.getFilterGroup(filterGroup);
      });

    }


    return (
      <div className="admin-modal__filters_wrapper">
        <h2>Filter</h2>
        <div className="admin-modal__filters_content">
          { content }
        </div>
      </div>
    );
  }
}

FilterSelector.propTypes = {
  // eslint-disable-next-line react/forbid-prop-types
  onFilterChanged: PropTypes.func.isRequired,
//   // eslint-disable-next-line react/forbid-prop-types
  adjustable_filter_type: PropTypes.bool.isRequired,
  filters_endpoint: PropTypes.string.isRequired,

};

export default FilterSelector;
