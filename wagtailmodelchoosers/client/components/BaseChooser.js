import PropTypes from 'prop-types';
import React from 'react';
import { SecondaryButton } from './Buttons';
import ModelPicker from './ModelPicker';
import { tr } from '../utils';

const STR = {
  choose: 'Choose',
  choose_again: 'Choose another',
  clear: 'Clear choice',
  edit: 'Edit'
};

const defaultProps = {
  display: 'title',
  filters: [],
  translations: {},
  pk_name: 'uuid',
  page_size: 10,
  page_size_param: 'page_size',
};

const propTypes = {
  initialValue: PropTypes.oneOfType([PropTypes.string, PropTypes.object]).isRequired,
  updateInputValue: PropTypes.func.isRequired,
  initial_display_value: PropTypes.string.isRequired,
  required: PropTypes.bool.isRequired,
  display: PropTypes.oneOfType([PropTypes.string, PropTypes.array]).isRequired,
  thumbnail: PropTypes.string,
  initial_thumbnail: PropTypes.string,
  pk_name: PropTypes.string,
  translations: PropTypes.object,
  label: PropTypes.string.isRequired,
  list_display: PropTypes.array.isRequired,
  has_list_filter: PropTypes.bool.isRequired,
  adjustable_filter_type: PropTypes.bool.isRequired,
  filters: PropTypes.array,
  endpoint: PropTypes.string.isRequired,
  edit_endpoint: PropTypes.string.isRequired,
  filters_endpoint: PropTypes.string.isRequired,
  page_size: PropTypes.number,
  page_size_param: PropTypes.string,
};

class BaseChooser extends React.Component {

  constructor(props) {
    super(props);

    const { display, initialValue, initial_display_value: initialDisplayValue, thumbnail, initial_thumbnail: initialThumbnail } = this.props;

    // If `initialValue` is an object (i.e. the item), use it directly,
    // otherwise create a new object and use the `initialValue` for the ID.
    const hasInitialObject = initialValue !== null && typeof initialValue === 'object';
    const selectedItem = hasInitialObject ? initialValue : {};
    const selectedId = hasInitialObject ? this.getItemPk(selectedItem) : initialValue;

    // Ensure the item has the required key for `display`.
    const displayKey = Array.isArray(display) ? display[0] : display;
    if (!(displayKey in selectedItem)) {
      selectedItem[displayKey] = initialDisplayValue;
    }

    if (!!thumbnail && !(thumbnail in selectedItem)) {
      selectedItem[thumbnail] = initialThumbnail;
    }

    this.state = {
      pickerVisible: false,
      selectedId,
      selectedItem,
      initialUrl: null,
    };

    this.showPicker = this.showPicker.bind(this);
    this.onClose = this.onClose.bind(this);
    this.onSelect = this.onSelect.bind(this);
    this.getItemPk = this.getItemPk.bind(this);
    this.getItemPreview = this.getItemPreview.bind(this);
    this.isOptional = this.isOptional.bind(this);
    this.getChooseButtons = this.getChooseButtons.bind(this);
    this.getThumbnail = this.getThumbnail.bind(this);
    this.clearPicker = this.clearPicker.bind(this);
    this.onEdit = this.onEdit.bind(this);
  }

  onEdit() {
    const { edit_endpoint } = this.props;
    window.open(edit_endpoint.replace("/0/", "/" + this.state.selectedId + "/"), '_blank');
  }

  onClose() {
    this.setState({
      pickerVisible: false,
    });
  }

  onSelect(id, item, url) {
    this.setState({
      selectedId: id,
      selectedItem: item,
      pickerVisible: false,
      initialUrl: url,
    }, () => {
      this.props.updateInputValue(item);
    });
  }

  getItemPk(item) {
    const { pk_name: pkName } = this.props;

    return item ? item[pkName] : null;
  }

  getItemPreview() {
    const { display } = this.props;
    const { selectedItem } = this.state;

    if (!selectedItem) {
      return '';
    }

    // Return first non-empty field if `display` is an Array.
    if (Array.isArray(display)) {
      let i;
      for (i = 0; i < display.length; i += 1) {
        const fieldName = display[i];
        if (fieldName in selectedItem && selectedItem[fieldName]) {
          return selectedItem[fieldName];
        }
      }
    }

    // Return the `display` field if available.
    if (display in selectedItem && selectedItem[display]) {
      return selectedItem[display];
    }

    // Return the object PK as default.
    return this.getItemPk(selectedItem);
  }

  getChooseButtons() {
    const { translations, edit_endpoint } = this.props;
    const { selectedId } = this.state;

    if (!selectedId) {
      return (
        <SecondaryButton
          onClick={this.showPicker}
          label={tr(STR, translations, 'choose')}
        />
      );
    }

    return (
      <span>
        <SecondaryButton
          onClick={this.showPicker}
          label={tr(STR, translations, 'choose_again')}
        />
        {}
        {!!edit_endpoint ? (
          <SecondaryButton
            onClick={this.onEdit}
            label={tr(STR, translations, 'edit')}
          />
        ) : null}

        {this.isOptional() ? (
          <SecondaryButton
            onClick={this.clearPicker}
            label={tr(STR, translations, 'clear')}
          />
        ) : null}
      </span>
    );
  }

  getThumbnail() {
    const { thumbnail } = this.props;
    const { selectedItem } = this.state;

    if (!selectedItem) {
      return (null);
    }

    if (!!thumbnail && !!selectedItem[thumbnail]) {
      return (<img className="model-chooser__thumb" src={selectedItem[thumbnail]}/>);
    }

    return (null);
  }

  isOptional() {
    const { required } = this.props;
    return !required;
  }

  showPicker() {
    this.setState({
      pickerVisible: true,
    });
  }

  clearPicker(e) {
    e.preventDefault();

    this.setState({
      selectedId: null,
      selectedItem: null,
      pickerVisible: false,
      initialUrl: null,
    }, () => {
      this.props.updateInputValue(null);
    });
  }

  render() {
    const { pickerVisible, initialUrl } = this.state;
    const {
      list_display: listDisplay,
      has_list_filter: hasListFilter,
      thumbnail,
      label,
      endpoint,
      filters_endpoint: filtersEndpoint,
      adjustable_filter_type,
      filters,
      pk_name: pkName,
      page_size: pageSize,
      page_size_param: pageSizeParam,
      translations,
    } = this.props;

    return (
      <div>
        <div className="model-chooser__container">
          {this.getThumbnail()}
          <span className="model-chooser__label">
            {this.getItemPreview()}
          </span>
          {this.getChooseButtons()}
        </div>
        {pickerVisible ? (
          <ModelPicker
            url={initialUrl}
            onClose={this.onClose}
            onSelect={this.onSelect}
            label={label}
            endpoint={endpoint}
            filters_endpoint={filtersEndpoint}
            has_list_filter={hasListFilter}
            thumbnail={thumbnail}
            filters={filters}
            list_display={listDisplay}
            pk_name={pkName}
            page_size={pageSize}
            page_size_param={pageSizeParam}
            adjustable_filter_type={adjustable_filter_type}
            translations={translations}
          />
        ) : null}
      </div>
    );
  }
}

BaseChooser.defaultProps = defaultProps;
BaseChooser.propTypes = propTypes;

export default BaseChooser;
