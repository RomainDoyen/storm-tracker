const classificationIcons = {
  'Dépression tropicale': '/static/images/icons/b_TropicalDepression.png',
  'Dépression tropicale': '/static/images/icons/b_TropicalDepression.png',
  'Tempête tropicale': '/static/images/icons/c_TropicalStorm.png',
  'Ouragan de catégorie 1': '/static/icons/icons/1.png',
  'Ouragan de catégorie 2': '/static/images/icons/2.png',
  'Ouragan de catégorie 3': '/static/images/icons/3.png',
  'Ouragan de catégorie 4': '/static/images/icons/4.png',
  'Ouragan de catégorie 5': '/static/images/icons/5.png',
  'Cyclone tropical de catégorie 1': '/static/images/icons/1.png',
  'Cyclone tropical de catégorie 2': '/static/images/icons/2.png',
  'Cyclone tropical de catégorie 3': '/static/images/icons/3.png',
  'Cyclone tropical de catégorie 4': '/static/images/icons/4.png',
  'Cyclone tropical de catégorie 5': '/static/images/icons/5.png',
};

export default function getIconUrl(classification) {
  return classificationIcons[classification] || '/static/images/hurricane.png';
}
